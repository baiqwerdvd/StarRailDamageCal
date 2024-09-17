from __future__ import annotations

import json
from pathlib import Path

import msgspec
from httpx import AsyncClient
from msgspec import convert

from ..exception import (
    InvalidUidError,
    MihomoModelError,
    MihomoQueueTimeoutError,
)
from ..mihomo.models import MihomoData

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
            path = save_path / str(uid)
            path.mkdir(parents=True, exist_ok=True)
            with Path.open(path / f"{uid!s}.json", "w") as file:
                _ = file.write(req.text)
        try:
            return convert(req.json(), type=MihomoData)
        except msgspec.ValidationError as e:
            if (
                req.text
                == '{"detail":"Queue timeout,please refer to https://discord.gg/pkdTJ9svEh for more infomation"}'
            ):
                raise MihomoQueueTimeoutError from e
            if req.text == '{"detail":"Invalid uid"}':
                raise InvalidUidError(uid) from e
            raise MihomoModelError(e) from e
        except json.decoder.JSONDecodeError as e:
            raise MihomoModelError(e) from e
