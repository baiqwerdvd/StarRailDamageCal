from starrail_damage_cal.cal_damage import cal_char_info, get_char_data
from starrail_damage_cal.damage.Avatar import AvatarInstance


async def test_get_damage_data_by_uid() -> None:
    # print(await api_to_dict("108069476"))
    char_data = await get_char_data(uid="100086290", avatar_name="希儿")
    print(char_data)

    char = await cal_char_info(char_data)
    print(char.add_attr)
    avatar = AvatarInstance(char)
    print(avatar.base_attr)
    print(avatar.attribute_bonus)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_get_damage_data_by_uid())
