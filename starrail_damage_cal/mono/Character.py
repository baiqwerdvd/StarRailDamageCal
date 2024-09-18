from collections import Counter
from typing import Dict, List

from ..map.SR_MAP_PATH import (
    EquipmentID2AbilityProperty,
    RelicSetSkill,
)
from ..model import MihomoCharacter


class Character:
    def __init__(self, card_prop: MihomoCharacter):
        self.char_level = card_prop.avatarLevel
        self.char_id = card_prop.avatarId
        self.char_name = card_prop.avatarName
        self.char_rank = card_prop.rank
        self.char_rarity = card_prop.avatarRarity
        self.char_element = card_prop.avatarElement
        self.char_promotion = card_prop.avatarPromotion
        self.char_skill = card_prop.avatarSkill
        self.extra_ability = card_prop.avatarExtraAbility
        self.attribute_bonus = card_prop.avatarAttributeBonus
        self.char_relic = card_prop.RelicInfo
        self.base_attributes = card_prop.baseAttributes
        self.equipment = card_prop.equipmentInfo
        self.rarity = card_prop.avatarRarity
        self.eidolons = card_prop.rankList
        self.add_attr: Dict[str, float] = {}

    async def get_equipment_info(self):
        base_attr = self.base_attributes
        equip = self.equipment
        ability_property = EquipmentID2AbilityProperty[str(equip.equipmentID)]
        equip_rank = equip.equipmentRank

        equip_ability_property = ability_property[str(equip_rank)]

        equip_add_base_attr = equip.baseAttributes
        base_attr.hp += equip_add_base_attr.hp
        base_attr.attack += +equip_add_base_attr.attack
        base_attr.defence += equip_add_base_attr.defence
        self.base_attributes = base_attr

        for equip_ability in equip_ability_property:
            property_type = equip_ability.PropertyType
            value = equip_ability.Value.Value
            self.add_attr[property_type] = value + self.add_attr.get(property_type, 0)

    async def get_char_attribute_bonus(self):
        attribute_bonus = self.attribute_bonus
        for bonus in attribute_bonus:
            status_add = bonus.statusAdd
            bonus_property = status_add.property_
            value = status_add.value
            self.add_attr[bonus_property] = value + self.add_attr.get(bonus_property, 0)

    async def get_relic_info(self):
        # 计算圣遗物效果
        set_id_list: List[int] = []
        for relic in self.char_relic:
            set_id_list.append(relic.SetId)
            # 处理主属性
            relic_property = relic.MainAffix.Property
            property_value = relic.MainAffix.Value
            self.add_attr[relic_property] = property_value + self.add_attr.get(
                relic_property,
                0,
            )
            # 处理副词条
            for sub in relic.SubAffixList:
                sub_property = sub.Property
                sub_value = sub.Value
                self.add_attr[sub_property] = sub_value + self.add_attr.get(
                    sub_property,
                    0,
                )
        # 处理套装属性
        set_id_dict = Counter(set_id_list)
        # logger.info(set_id_dict.most_common())
        for item in set_id_dict.most_common():
            set_property = ""
            set_id = item[0]
            count = item[1]
            set_value = 0
            if count >= 2:
                status_add = RelicSetSkill[str(set_id)].get("2", None)
                if status_add:
                    set_property = status_add.Property
                    set_value = status_add.Value
                    if set_property != "":
                        self.add_attr[set_property] = set_value + self.add_attr.get(
                            set_property,
                            0,
                        )
            if count == 4:
                status_add = RelicSetSkill[str(set_id)].get("4", None)
                if status_add:
                    set_property = status_add.Property
                    set_value = status_add.Value
                    if set_property != "":
                        self.add_attr[set_property] = set_value + self.add_attr.get(
                            set_property,
                            0,
                        )
