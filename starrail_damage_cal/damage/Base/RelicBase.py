from abc import abstractmethod
from typing import Dict

from ...logger import logger
from ...map.SR_MAP_PATH import RelicSetSkill, RelicSetStatusAdd
from ...model import Relic


class SingleRelic:
    def __init__(self, relic: Relic):
        self.raw_relic = relic
        self.relic_id = relic.relicId
        self.set_id = relic.SetId
        self.relic_type = relic.Type
        self.relic_level = relic.Level
        self.relic_attribute_bonus: Dict[str, float] = {}

    def get_attribute_(self):
        # MainAffix
        if self.raw_relic.MainAffix.Property in self.relic_attribute_bonus:
            self.relic_attribute_bonus[self.raw_relic.MainAffix.Property] += (
                self.raw_relic.MainAffix.Value
            )
        else:
            self.relic_attribute_bonus[self.raw_relic.MainAffix.Property] = (
                self.raw_relic.MainAffix.Value
            )

        # SubAffix
        if self.raw_relic.SubAffixList:
            for sub_affix in self.raw_relic.SubAffixList:
                sub_affix_property = sub_affix.Property
                value = sub_affix.Value
                if sub_affix_property in self.relic_attribute_bonus:
                    self.relic_attribute_bonus[sub_affix_property] += value
                else:
                    self.relic_attribute_bonus[sub_affix_property] = value


class BaseRelicSetSkill:
    setId: int
    pieces2: bool = False
    pieces4: bool = False

    def __init__(self, set_id: int, count: int):
        self.setId = set_id
        if count >= 2:
            self.pieces2 = True
            logger.info(f"Relic {set_id} 2 pieces set activated")
        if count == 4:
            self.pieces4 = True
            logger.info(f"Relic {set_id} 4 pieces set activated")
        self.relicSetAttribute = self.set_skill_property_ability()

    @abstractmethod
    async def check(
        self,
        base_attr: Dict[str, float],
        attribute_bonus: Dict[str, float],
    ) -> bool: ...

    @abstractmethod
    async def set_skill_ability(
        self,
        base_attr: Dict[str, float],
        attribute_bonus: Dict[str, float],
    ) -> Dict[str, float]:
        """战斗加成属性, 与 set_skill_property() 互斥"""
        ...

    def set_skill_property_ability(self):
        def add_relic_set_attribute(status_add: RelicSetStatusAdd):
            set_property = status_add.Property
            set_value = status_add.Value
            if set_property != "":
                relic_set_attribute[set_property] = (
                    relic_set_attribute.get(set_property, 0) + set_value
                )

        relic_set_attribute: Dict[str, float] = {}
        if self.pieces2:
            status_add = RelicSetSkill[str(self.setId)].get("2", None)
            if status_add:
                add_relic_set_attribute(status_add)

        if self.pieces4:
            status_add = RelicSetSkill[str(self.setId)].get("4", None)
            if status_add:
                add_relic_set_attribute(status_add)

        return relic_set_attribute
