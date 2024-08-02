import json
from typing import List, Union

from starrail_damage_cal.cal_damage import DamageCal
from starrail_damage_cal.to_data import api_to_dict


async def test_get_damage_data_by_uid() -> None:
    # print(await api_to_dict("108069476"))
    data = await DamageCal.get_damage_data_by_uid(uid="108069476", avatar_name="流萤")
    if isinstance(data, Union[List, dict]):
        print(json.dumps(data, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_get_damage_data_by_uid())
