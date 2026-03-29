# ruff: noqa: S101

import json
from pathlib import Path

import pytest

from starrail_damage_cal import DamageCal


def load_test_data() -> dict:
    return json.loads(Path("test/test.json").read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_get_damage_data_by_mihomo_raw():
    data = await DamageCal.get_damage_data_by_mihomo_raw(
        mihomo_raw=load_test_data(),
        avatar_name="镜流",
    )

    assert isinstance(data, list)
    assert data
    assert data[0]["name"] == "普攻"
    assert data[0]["damagelist"]


@pytest.mark.asyncio
async def test_get_all_damage_data_by_mihomo_raw():
    data = await DamageCal.get_all_damage_data_by_mihomo_raw(mihomo_raw=load_test_data())

    assert isinstance(data, dict)
    assert "1212" in data
    assert isinstance(data["1212"], list)
    assert data["1212"][0]["name"] == "普攻"
