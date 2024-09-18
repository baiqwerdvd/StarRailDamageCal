import json
from pathlib import Path
from typing import Dict

from ..damage.AvatarDamage.AvatarDamage import AvatarDamage
from ..damage.Base.AvatarBase import BaseAvatarinfo
from ..damage.Base.model import DamageInstance
from ..damage.Base.RelicBase import SingleRelic
from ..damage.Relic.Relic import RelicSet
from ..damage.Weapon.Weapon import Weapon
from ..mono.Character import Character

Excel_path = Path(__file__).parent
with Path.open(Excel_path / "Excel" / "SkillData.json", encoding="utf-8") as f:
    skill_dict = json.load(f)


class AvatarInstance:
    def __init__(self, raw_data: Character):
        self.raw_data = DamageInstance(raw_data)
        self.avatardamage = AvatarDamage.create(
            self.raw_data.avatar,
            self.raw_data.skill,
        )
        self.avatar = BaseAvatarinfo(self.raw_data.avatar)
        if self.raw_data.weapon is None:
            self.weapon = None
        else:
            self.weapon = Weapon.create(self.raw_data.weapon)
        self.relic_set = RelicSet().create(self.raw_data.relic)

        self.base_attr = self.cal_role_base_attr()
        self.attribute_bonus: Dict[str, float] = {}

        self.cal_relic_attr_add()
        self.cal_avatar_attr_add()
        self.cal_avatar_eidolon_add()
        if self.weapon is not None:
            self.cal_weapon_attr_add()

    def merge_attribute_bonus(self, add_attribute: Dict[str, float]):
        for attribute in add_attribute:
            if attribute in self.attribute_bonus:
                self.attribute_bonus[attribute] += add_attribute[attribute]
            else:
                self.attribute_bonus[attribute] = add_attribute[attribute]

    def cal_role_base_attr(self):
        base_attr: Dict[str, float] = {}
        avatar_attribute = self.avatar.avatar_attribute
        for attr_name, attr_value in avatar_attribute.items():
            if attr_name in base_attr:
                base_attr[attr_name] += attr_value
            else:
                base_attr[attr_name] = attr_value

        if self.weapon is None:
            return base_attr

        weapon_attribute = self.weapon.weapon_base_attribute
        for attr_name, attr_value in weapon_attribute.items():
            if attr_name in base_attr:
                base_attr[attr_name] += attr_value
            else:
                base_attr[attr_name] = attr_value
        return base_attr

    def cal_relic_attr_add(self):
        # 单件属性
        for relic_type in self.relic_set.__dict__:
            if type(self.relic_set.__dict__[relic_type]) == SingleRelic:
                relic: SingleRelic = self.relic_set.__dict__[relic_type]
                self.merge_attribute_bonus(relic.relic_attribute_bonus)

        # 套装面板加成属性
        for set_skill in self.relic_set.SetSkill:
            self.merge_attribute_bonus(set_skill.relicSetAttribute)

    def cal_avatar_eidolon_add(self):
        if self.avatardamage is None:
            return
        self.merge_attribute_bonus(self.avatardamage.eidolon_attribute)
        self.merge_attribute_bonus(self.avatardamage.extra_ability_attribute)

    def cal_avatar_attr_add(self):
        attribute_bonus = self.avatar.avatar_attribute_bonus
        if attribute_bonus:
            for bonus in attribute_bonus:
                status_add = bonus.statusAdd
                bonus_property = status_add.property_
                value = status_add.value
                if bonus_property in self.attribute_bonus:
                    self.attribute_bonus[bonus_property] += value
                else:
                    self.attribute_bonus[bonus_property] = value

    def cal_weapon_attr_add(self):
        if self.weapon is None:
            return
        self.merge_attribute_bonus(self.weapon.weapon_attribute)

    async def get_damage_info(self):
        Ultra_Use = self.avatar.Ultra_Use()
        if self.weapon is not None:
            self.attribute_bonus = await self.weapon.weapon_ability(
                Ultra_Use,
                self.base_attr,
                self.attribute_bonus,
            )
        for set_skill in self.relic_set.SetSkill:
            self.attribute_bonus = await set_skill.set_skill_ability(
                self.base_attr,
                self.attribute_bonus,
            )

        return await self.avatardamage.getdamage(self.base_attr, self.attribute_bonus)
