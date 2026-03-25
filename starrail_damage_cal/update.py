import asyncio
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import aiohttp

from . import data_paths
from .logger import logger

VERSION_URL = "https://starrail.wget.es/version.json"
SKIPPED_FILES = {"light_cone_ranks.json"}


def calc_sha256(file_path: Path) -> str:
    """计算文件 SHA256"""
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def managed_relative_path(file_name: str) -> Path:
    if file_name.endswith("_mapping.json"):
        return Path("map") / "data" / file_name
    return Path("excel") / file_name


def iter_managed_files(version_data: dict[str, Any]) -> list[tuple[str, Path]]:
    managed_files: list[tuple[str, Path]] = []
    for file_name in version_data.get("file_names", []):
        if file_name in SKIPPED_FILES:
            continue
        managed_files.append((file_name, managed_relative_path(file_name)))
    return managed_files


def read_local_version_data() -> dict[str, Any] | None:
    version_file = data_paths.resolve_version_file()
    if not version_file.exists():
        return None

    try:
        with version_file.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning("本地version.json文件损坏, 将重新获取全部数据文件")
        return None


def write_json_atomically(file_path: Path, data: dict[str, Any]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_name(f"{file_path.name}.tmp")
    try:
        with temp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        temp_path.replace(file_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def local_file_is_outdated(file_name: str, remote_data: dict[str, Any]) -> bool:
    local_path = data_paths.resolve_data_path(managed_relative_path(file_name))
    if not local_path.exists():
        return True

    expected_sha = remote_data.get("files", {}).get(file_name, {}).get("sha256")
    if expected_sha is None:
        return True
    return calc_sha256(local_path) != expected_sha


def collect_outdated_files(remote_data: dict[str, Any]) -> list[str]:
    outdated_files = []
    for file_name, _ in iter_managed_files(remote_data):
        if local_file_is_outdated(file_name, remote_data):
            outdated_files.append(file_name)
    return outdated_files


def cleanup_stale_runtime_files(version_data: dict[str, Any]) -> None:
    runtime_root = data_paths.get_runtime_base_dir()
    expected_files = {
        relative_path for _, relative_path in iter_managed_files(version_data)
    }

    for relative_dir in (Path("excel"), Path("map") / "data"):
        runtime_dir = runtime_root / relative_dir
        if not runtime_dir.exists():
            continue
        for file_path in runtime_dir.glob("*.json"):
            if file_path.relative_to(runtime_root) not in expected_files:
                file_path.unlink()


def refresh_loaded_data() -> None:
    excel_module = sys.modules.get("starrail_damage_cal.excel.model")
    if excel_module is not None:
        excel_module.reload_excel_data()

    map_module = sys.modules.get("starrail_damage_cal.map.SR_MAP_PATH")
    if map_module is not None:
        map_module.reload_map_data()


async def fetch_json(session: aiohttp.ClientSession, url: str) -> dict[str, Any]:
    """请求并返回 JSON 响应"""
    async with session.get(url) as resp:
        resp.raise_for_status()
        return await resp.json()


async def fetch_file(
    session: aiohttp.ClientSession,
    url: str,
    save_path: Path,
) -> None:
    """下载文件并原子替换到目标位置"""
    save_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = save_path.with_name(f"{save_path.name}.tmp")

    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            content = await resp.read()

        with temp_path.open("wb") as f:
            f.write(content)
        temp_path.replace(save_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    logger.info(f"下载完成: {save_path.name}")


async def download_files(
    session: aiohttp.ClientSession,
    version_data: dict[str, Any],
    file_names: list[str],
) -> int:
    base_url = f"https://starrail.wget.es/{version_data['version']}"
    tasks = []

    for file_name in file_names:
        relative_path = managed_relative_path(file_name)
        target_path = data_paths.runtime_path(relative_path)
        tasks.append(
            asyncio.create_task(
                fetch_file(session, f"{base_url}/{file_name}", target_path)
            )
        )

    await asyncio.gather(*tasks)
    return len(file_names)


async def download_all_files(
    session: aiohttp.ClientSession,
    version_data: dict[str, Any],
) -> int:
    """全量下载所有受控文件"""
    managed_files = [file_name for file_name, _ in iter_managed_files(version_data)]
    return await download_files(session, version_data, managed_files)


async def selective_update(
    session: aiohttp.ClientSession,
    new_data: dict[str, Any],
    old_data: dict[str, Any] | None = None,
) -> int:
    """检查各文件sha变化并下载需要的文件"""
    del old_data
    outdated_files = collect_outdated_files(new_data)
    return await download_files(session, new_data, outdated_files)


def persist_version_data(remote_data: dict[str, Any]) -> None:
    cleanup_stale_runtime_files(remote_data)
    write_json_atomically(data_paths.runtime_path("version.json"), remote_data)
    refresh_loaded_data()


async def update_resource() -> str:
    """
    异步接口函数
    负责根据远程version.json同步资源文件
    """
    logger.info("开始检查星铁数据文件更新...")
    async with aiohttp.ClientSession() as session:
        remote_data = await fetch_json(session, VERSION_URL)
        local_data = read_local_version_data()

        if local_data is None:
            await download_all_files(session, remote_data)
            persist_version_data(remote_data)
            msg = "本地没有可用version.json文件, 已重新获取全部数据文件"
            logger.info(msg)
            return msg

        same_version = local_data.get("version") == remote_data.get("version")
        same_generated_time = local_data.get("generated_at") == remote_data.get(
            "generated_at"
        )
        outdated_files = collect_outdated_files(remote_data)

        if same_version and same_generated_time and not outdated_files:
            msg = "数据文件已是最新"
            logger.info(msg)
            return msg

        if not same_version:
            await download_all_files(session, remote_data)
            persist_version_data(remote_data)
            msg = "检测到版本更新, 数据文件已完成更新"
            logger.info(msg)
            return msg

        updated_count = await download_files(session, remote_data, outdated_files)
        persist_version_data(remote_data)

        if same_generated_time:
            msg = f"检测到本地数据文件缺失或损坏, 本次已更新{updated_count}个文件"
        else:
            msg = f"检测到数据文件更新, 本次已更新{updated_count}个文件"

        logger.info(msg)
        return msg
