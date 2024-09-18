from ..excel.model import CharAlias
from ..map.SR_MAP_PATH import (
    avatarId2Name,
)


def name_to_avatar_id(name: str) -> str:
    avatar_id = ""
    for i in avatarId2Name:
        if avatarId2Name[i] == name:
            avatar_id = i
            break
    return avatar_id


def alias_to_char_name(char_name: str) -> str:
    for i in CharAlias["characters"]:
        if char_name in CharAlias["characters"][i]:
            return CharAlias["characters"][i][0]
    return char_name
