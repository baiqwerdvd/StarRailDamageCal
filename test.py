import json
from typing import List, Union

from starrail_damage_cal.cal_damage import DamageCal, cal_char_info, get_char_data
from starrail_damage_cal.damage.Avatar import AvatarInstance
from starrail_damage_cal.to_data import api_to_dict


async def test_get_damage_data_by_uid() -> None:
    # print(await api_to_dict("108069476"))
    char_data = await get_char_data(uid="100086290", avatar_name="希儿")
    print(json.dumps(char_data, ensure_ascii=False, indent=4))

    char = await cal_char_info(char_data)
    avatar = AvatarInstance(char)
    print(avatar.base_attr)
    print(avatar.attribute_bonus)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_get_damage_data_by_uid())
