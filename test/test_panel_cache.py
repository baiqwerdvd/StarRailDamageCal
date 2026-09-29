# ruff: noqa: S101

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from msgspec import json as msgjson

from starrail_damage_cal.model import MihomoCharacter
from starrail_damage_cal.to_data import _get_mys_data, get_data


@pytest.mark.asyncio
@pytest.mark.parametrize("source", ["mihomo", "mys"])
async def test_source_and_time_survive_disk_roundtrip_and_legacy_cache(
    tmp_path: Path, source: str
):
    if source == "mihomo":
        convert = get_data
        avatar = SimpleNamespace(
            avatarId=1001,
            promotion=0,
            level=20,
            skillTreeList=[],
            relicList=[],
            rank=0,
            equipment=None,
            enhancedId=0,
        )
    else:
        convert = _get_mys_data
        avatar = SimpleNamespace(
            id=1302,
            level=20,
            promotion=0,
            cur_enhanced_id=0,
            skills=[],
            relics=[],
            ornaments=[],
            ranks=[],
            equip=None,
        )
    before = datetime.now(UTC).replace(microsecond=0)
    char, name = await convert(avatar, "tester", "100000001", tmp_path)
    raw = (tmp_path / "100000001" / f"{name}.json").read_bytes()
    data = msgjson.decode(raw)
    assert data["source"] == source
    updated = datetime.fromisoformat(data["updated_at"])
    assert updated.utcoffset().total_seconds() == 0
    assert updated >= before
    loaded = msgjson.decode(raw, type=MihomoCharacter)
    assert loaded.source == source
    assert loaded.updated_at == char.updated_at
    data.pop("source")
    data.pop("updated_at")
    old = msgjson.decode(msgjson.encode(data), type=MihomoCharacter)
    assert old.source == ""
    assert old.updated_at == ""
