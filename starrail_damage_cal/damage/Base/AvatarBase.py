import json
from abc import abstractmethod
from pathlib import Path
from typing import List, Tuple, Union

import msgspec
from msgspec import Struct

from ...damage.Base.model import (
    DamageInstanceAvatar,
)
from ...damage.Base.SkillBase import BaseSkills
from ...excel.model import AvatarPromotionConfig
from ...model import MihomoAvatarSkill

path = Path(__file__).parent.parent
with Path.open(path / "Excel" / "SkillData.json", encoding="utf-8") as f:
    skill_dict = json.load(f)


class BaseAvatarAttribute(Struct):
    attack: float
    defence: float
    hp: float
    speed: float
    CriticalChanceBase: float
    CriticalDamageBase: float
    BaseAggro: float

    def items(self) -> List[Tuple[str, float]]:
        return [
            ("attack", self.attack),
            ("defence", self.defence),
            ("hp", self.hp),
            ("speed", self.speed),
            ("CriticalChanceBase", self.CriticalChanceBase),
            ("CriticalDamageBase", self.CriticalDamageBase),
            ("BaseAggro", self.BaseAggro),
        ]


class BaseAvatarBuff:
    @classmethod
    def create(cls, char: DamageInstanceAvatar, skills: List[MihomoAvatarSkill]):
        del skills
        buff = cls()
        buff.extra_ability_id = []
        if char.extra_ability:
            for extra_ability in char.extra_ability:
                buff.extra_ability_id.append(extra_ability.extraAbilityId)
        return buff

    @abstractmethod
    async def Technique(self): ...

    @abstractmethod
    async def eidolons(self): ...

    @abstractmethod
    async def extra_ability(self): ...


class BaseAvatarinfo:
    def __init__(self, char: DamageInstanceAvatar):
        self.avatar_id = char.id_
        self.avatar_level = char.level
        self.avatar_rank = char.rank
        self.avatar_element = char.element
        self.avatar_promotion = char.promotion
        self.avatar_attribute_bonus = char.attribute_bonus
        self.avatar_extra_ability = char.extra_ability
        self.avatar_attribute = self.get_attribute()

    def get_attribute(self):
        return build_base_avatar_attribute(
            avatar_id=self.avatar_id,
            avatar_promotion=self.avatar_promotion,
            avatar_level=self.avatar_level,
        )

    def Ultra_Use(self):
        skill_info = skill_dict[str(self.avatar_id)]["Ultra_Use"][0]
        return msgspec.convert(skill_info, type=float)


class BaseAvatar:
    def __init__(self, char: DamageInstanceAvatar, skills: List[MihomoAvatarSkill]):
        self.Skill = BaseSkills.create(char=char, skills=skills)
        self.Buff = BaseAvatarBuff.create(char=char, skills=skills)
        self.avatar_id = char.id_
        self.avatar_level = char.level
        self.avatar_rank = char.rank
        self.avatar_element = char.element
        self.avatar_promotion = char.promotion
        self.avatar_attribute_bonus = char.attribute_bonus
        self.avatar_extra_ability = char.extra_ability
        self.avatar_attribute = self.get_attribute()

    def get_attribute(self):
        return build_base_avatar_attribute(
            avatar_id=self.avatar_id,
            avatar_promotion=self.avatar_promotion,
            avatar_level=self.avatar_level,
        )

    def Skill_Info(self, skill_type: str):
        skill_info = skill_dict[str(self.avatar_id)]["skillList"][skill_type]
        return msgspec.convert(skill_info, type=List[Union[str, int]])

    def Skill_num(self, skill: Union[str, int], skill_type: str):
        skill_level = 0
        if skill == "Normal":
            skill_level = self.Skill.Normal_.level - 1
        if skill == "BPSkill":
            skill_level = self.Skill.BPSkill_.level - 1
        if skill == "Ultra":
            skill_level = self.Skill.Ultra_.level - 1
        if skill == "Talent":
            skill_level = self.Skill.Talent_.level - 1
        skill_info = skill_dict[str(self.avatar_id)][skill_type][skill_level]
        return msgspec.convert(skill_info, type=float)


def get_avatar_promotion_config(avatar_id: int, avatar_promotion: int):
    for avatar in AvatarPromotionConfig:
        if avatar.AvatarID == avatar_id and (avatar.Promotion or 0) == avatar_promotion:
            return avatar

    msg = f"AvatarPromotionConfig not found: {avatar_id} promotion {avatar_promotion}"
    raise ValueError(msg)


def build_base_avatar_attribute(
    avatar_id: int,
    avatar_promotion: int,
    avatar_level: int,
) -> BaseAvatarAttribute:
    promotion = get_avatar_promotion_config(avatar_id, avatar_promotion)

    return BaseAvatarAttribute(
        attack=promotion.AttackBase.Value + promotion.AttackAdd.Value * (avatar_level - 1),
        defence=(
            promotion.DefenceBase.Value
            + promotion.DefenceAdd.Value * (avatar_level - 1)
        ),
        hp=promotion.HPBase.Value + promotion.HPAdd.Value * (avatar_level - 1),
        speed=promotion.SpeedBase.Value,
        CriticalChanceBase=promotion.CriticalChance.Value,
        CriticalDamageBase=promotion.CriticalDamage.Value,
        BaseAggro=promotion.BaseAggro.Value,
    )
