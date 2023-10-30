import json
from pathlib import Path
from typing import Dict

import pytest

from starrail_damage_cal import DamageCal

with Path.open(Path("test/test.json"), encoding="utf-8") as f:
    test_data = json.load(f)


@pytest.mark.asyncio()
async def test_get_damage_data_by_uid():
    data = await DamageCal.get_damage_data_by_uid(uid="100086290", avatar_name="希儿")
    if isinstance(data, Dict):
        print(json.dumps(data, ensure_ascii=False, indent=4))


@pytest.mark.asyncio()
async def test_get_damage_data_by_mihomo_raw():
    data = await DamageCal.get_damage_data_by_mihomo_raw(
        mihomo_raw=test_data, avatar_name="希儿"
    )
    if isinstance(data, Dict):
        print(json.dumps(data, ensure_ascii=False, indent=4))


@pytest.mark.asyncio()
async def test_get_all_damage_data_by_mihomo_raw():
    data = await DamageCal.get_all_damage_data_by_mihomo_raw(mihomo_raw=test_data)
    if isinstance(data, Dict):
        print(json.dumps(data, ensure_ascii=False, indent=4))


@pytest.mark.asyncio()
async def test_get_all_damage_data_by_uid():
    data = await DamageCal.get_all_damage_data_by_uid(uid="100086290")
    if isinstance(data, Dict):
        print(json.dumps(data, ensure_ascii=False, indent=4))
