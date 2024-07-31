import json
from typing import List, Union

from starrail_damage_cal.cal_damage import DamageCal


async def test_get_damage_data_by_uid() -> None:
    data = await DamageCal.get_all_damage_data_by_uid(uid="100111010")
    if isinstance(data, Union[List, dict]):
        print(json.dumps(data, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_get_damage_data_by_uid())
