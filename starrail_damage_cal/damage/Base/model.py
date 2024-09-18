from typing import List, Union

from msgspec import Struct, field

from ...model import (
    MihomoAvatarAttributeBonus,
    MihomoAvatarExtraAbility,
    MihomoAvatarSkill,
    Relic,
)
from ...mono.Character import Character


class DamageInstanceWeapon(Struct):
    id_: int = field(name="id")
    level: int
    rank: int
    promotion: int


class DamageInstanceAvatar(Struct):
    id_: int = field(name="id")
    level: int
    rank: int
    element: str
    promotion: int
    attribute_bonus: List[MihomoAvatarAttributeBonus]
    extra_ability: List[MihomoAvatarExtraAbility]


class DamageInstance:
    avatar: DamageInstanceAvatar
    weapon: Union[DamageInstanceWeapon, None]
    relic: List[Relic]
    skill: List[MihomoAvatarSkill]

    def __init__(self, char: Character):
        self.avatar = DamageInstanceAvatar(
            id_=char.char_id,
            level=char.char_level,
            rank=char.char_rank,
            element=char.char_element,
            promotion=char.char_promotion,
            attribute_bonus=char.attribute_bonus,
            extra_ability=char.extra_ability,
        )
        self.weapon = DamageInstanceWeapon(
            id_=char.equipment.equipmentID,
            level=char.equipment.equipmentLevel,
            rank=char.equipment.equipmentRank,
            promotion=char.equipment.equipmentPromotion,
        )
        self.relic = char.char_relic
        self.skill = char.char_skill
