from __future__ import annotations

from httpx import AsyncClient
from msgspec import convert

from starrail_damage_cal.mihomo.models import MihomoData

_HEADER = {"User-Agent": "StarRailDamageCal/"}


async def get_char_card_info(uid: str) -> MihomoData:
    async with AsyncClient(
        base_url="http://api.mihomo.me",
        headers=_HEADER,
        timeout=30,
    ) as client:
        req = await client.get(f"/sr_info/{uid}")
        return convert(req.json(), type=MihomoData)
