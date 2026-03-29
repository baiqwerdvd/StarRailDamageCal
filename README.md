# StarRailDamageCal

`StarRailDamageCal` 是一个基于崩坏：星穹铁道角色面板数据的伤害计算库。

当前仓库主要提供三类能力：

- 将 Mihomo / 米游社角色数据转换为统一的内部模型
- 基于角色、光锥、遗器与命座信息计算技能伤害
- 更新本地 Excel / 映射资源文件

## 环境要求

- Python `3.11+`

## 安装

使用 `uv`：

```bash
uv sync --group test --group lint
```

使用 `pdm`：

```bash
pdm install -G test -G lint
```

## 快速使用

按 UID 读取公开展示柜并计算指定角色：

```python
import asyncio

from starrail_damage_cal import DamageCal


async def main() -> None:
    data = await DamageCal.get_damage_data_by_uid(
        uid="100086290",
        avatar_name="镜流",
    )
    print(data)


asyncio.run(main())
```

直接使用 Mihomo 原始数据：

```python
import asyncio
import json
from pathlib import Path

from starrail_damage_cal import DamageCal


async def main() -> None:
    mihomo_raw = json.loads(Path("test/test.json").read_text(encoding="utf-8"))
    data = await DamageCal.get_damage_data_by_mihomo_raw(
        mihomo_raw=mihomo_raw,
        avatar_name="镜流",
    )
    print(data)


asyncio.run(main())
```

## 更新资源文件

项目内置了资源更新接口，会将新版本数据覆盖到运行时目录：

```python
import asyncio

from starrail_damage_cal.update import update_resource


async def main() -> None:
    print(await update_resource())


asyncio.run(main())
```

默认运行时目录是 `~/.starrail_damage_cal`，也可以通过环境变量 `STARRAIL_DAMAGE_CAL_DATA_DIR` 指定。

## 测试

```bash
python -m pytest
```

测试默认使用仓库内的离线样例数据，不依赖在线 UID。

## 当前限制

- 角色、光锥、遗器的部分条件性效果仍然采用静态假设，而不是完整战斗时序模拟
- 如果游戏新角色尚未接入对应伤害模型，会显式抛出 `UnsupportedAvatarError`
- 在线 UID 计算依赖外部数据源的可用性
