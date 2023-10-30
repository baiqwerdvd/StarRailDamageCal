import json
from typing import List

from starrail_damage_cal.cal_damage import DamageCal


async def test_get_damage_data_by_uid():
    data = await DamageCal.get_damage_data_by_uid(uid="100086290", avatar_name="希儿")
    if isinstance(data, List):
        print(json.dumps(data, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_get_damage_data_by_uid())
