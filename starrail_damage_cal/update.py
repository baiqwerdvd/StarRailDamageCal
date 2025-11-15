import aiohttp
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Dict, Any
from .logger import logger

VERSION_URL = "https://starrail.wget.es/version.json"
BASE_DIR = Path(__file__).resolve().parent
LOCAL_VERSION_FILE = BASE_DIR / "version.json"
MAP_DATA_DIR = BASE_DIR / "map" / "data"
EXCEL_DIR = BASE_DIR / "excel"

def calc_sha256(file_path: Path) -> str:
    """计算文件 SHA256"""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

async def fetch_json(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    """请求并返回 JSON 响应"""
    async with session.get(url) as resp:
        resp.raise_for_status()
        return await resp.json()

async def fetch_file(session: aiohttp.ClientSession, url: str, save_path: Path):
    """下载文件"""
    save_path.parent.mkdir(parents=True, exist_ok=True)
    async with session.get(url) as resp:
        resp.raise_for_status()
        content = await resp.read()
        with open(save_path, "wb") as f:
            f.write(content)
    logger.info(f"下载完成: {save_path.name}")

async def download_all_files(session: aiohttp.ClientSession, version_data: Dict[str, Any]) -> int:
    """全量下载所有受控文件"""
    download_count = 0
    base_url = f"https://starrail.wget.es/{version_data['version']}"
    tasks = []

    for fname in version_data["file_names"]:
        if fname == "light_cone_ranks.json":
            continue  # 跳过该文件
        
        # 路径选择
        if fname.endswith("_mapping.json"):
            path = MAP_DATA_DIR / fname
        else:
            path = EXCEL_DIR / fname

        url = f"{base_url}/{fname}"

        tasks.append(asyncio.create_task(fetch_file(session, url, path)))
        download_count += 1

    await asyncio.gather(*tasks)
    return download_count

async def selective_update(session: aiohttp.ClientSession, new_data: Dict[str, Any], old_data: Dict[str, Any]) -> int:
    """检查各文件sha变化并下载需要的文件"""
    base_url = f"https://starrail.wget.es/{new_data['version']}"
    updated = 0
    tasks = []

    for fname in new_data["file_names"]:
        if fname == "light_cone_ranks.json":
            continue

        new_info = new_data["files"].get(fname, {})

        if fname.endswith("_mapping.json"):
            path = MAP_DATA_DIR / fname
        else:
            path = EXCEL_DIR / fname

        # 本地不存在或sha不同则更新
        if not path.exists() or calc_sha256(path) != new_info.get("sha256"):
            tasks.append(asyncio.create_task(fetch_file(session, f"{base_url}/{fname}", path)))
            updated += 1

    await asyncio.gather(*tasks)
    return updated

async def update_resource() -> str:
    """
    异步接口函数
    负责根据远程version.json同步资源文件
    """
    logger.info("开始检查星铁数据文件更新...")
    async with aiohttp.ClientSession() as session:
        remote_data = await fetch_json(session, VERSION_URL)

        # 本地无 version.json → 全量拉取
        if not LOCAL_VERSION_FILE.exists():
            with open(LOCAL_VERSION_FILE, "w", encoding="utf-8") as f:
                json.dump(remote_data, f, ensure_ascii=False, indent=2)
            await download_all_files(session, remote_data)
            msg = "本地没有version.json文件已重新获取全部数据文件"
            logger.info(msg)
            return msg

        # 本地存在version.json
        with open(LOCAL_VERSION_FILE, "r", encoding="utf-8") as f:
            local_data = json.load(f)

        same_version = local_data.get("version") == remote_data.get("version")
        same_generated_time = local_data.get("generated_at") == remote_data.get("generated_at")

        # 已是最新
        if same_version and same_generated_time:
            msg = "数据文件已是最新"
            logger.info(msg)
            return msg

        # 版本号不同 → 全量更新
        if not same_version:
            with open(LOCAL_VERSION_FILE, "w", encoding="utf-8") as f:
                json.dump(remote_data, f, ensure_ascii=False, indent=2)
            await download_all_files(session, remote_data)
            msg = "检测到版本更新，数据文件已完成更新"
            logger.info(msg)
            return msg

        # version相同 generated_at不同 → 对比sha256判断局部更新
        updated_count = await selective_update(session, remote_data, local_data)
        with open(LOCAL_VERSION_FILE, "w", encoding="utf-8") as f:
            json.dump(remote_data, f, ensure_ascii=False, indent=2)
        msg = f"检测到数据文件更新，本次已更新{updated_count}个文件"
        logger.info(msg)
        return msg