from __future__ import annotations

from pathlib import Path

from httpx import AsyncClient
from msgspec import convert

from starrail_damage_cal.mihomo.models import MihomoData

_HEADER = {"User-Agent": "StarRailDamageCal/"}


async def get_char_card_info(
    uid: str,
    save_path: Path | None = None,
) -> MihomoData:
    async with AsyncClient(
        base_url="http://api.mihomo.me",
        headers=_HEADER,
        timeout=30,
    ) as client:
        req = await client.get(f"/sr_info/{uid}")
        if save_path:
            save_path.mkdir(parents=True, exist_ok=True)
            with Path.open(save_path / uid / f"{uid!s}.json", "w") as file:
                file.write(req.text)
        return convert(req.json(), type=MihomoData)
