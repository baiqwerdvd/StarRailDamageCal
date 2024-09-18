from abc import abstractmethod
from typing import Dict, List, Tuple

from msgspec import Struct

from ...damage.Base.model import DamageInstanceWeapon
from ...excel.model import EquipmentPromotionConfig
from ...map.SR_MAP_PATH import EquipmentID2AbilityProperty


class BaseWeaponAttribute(Struct):
    hp: float
    attack: float
    defence: float

    def items(self) -> List[Tuple[str, float]]:
        return [
            ("hp", self.hp),
            ("attack", self.attack),
            ("defence", self.defence),
        ]


class BaseWeapon:
    def __init__(self, weapon: DamageInstanceWeapon):
        self.weapon_id = weapon.id_
        self.weapon_level = weapon.level
        self.weapon_rank = weapon.rank
        self.weapon_promotion = weapon.promotion
        self.weapon_base_attribute = self.get_attribute()
        self.weapon_attribute: Dict[str, float] = {}
        self.weapon_property_ability()

    @abstractmethod
    async def weapon_ability(
        self, Ultra_Use: float, base_attr: Dict[str, float], attribute_bonus: Dict
    ) -> Dict[str, float]:
        """战斗加成属性, 与 weapon_property_ability() 互斥"""
        ...

    def weapon_property_ability(self):
        """面板加成属性, 与 weapon_ability() 互斥"""
        ability_property = EquipmentID2AbilityProperty[str(self.weapon_id)]
        equip_ability_property = ability_property[str(self.weapon_rank)]
        for equip_ability in equip_ability_property:
            property_type = equip_ability.PropertyType
            value = equip_ability.Value.Value
            if property_type in self.weapon_attribute:
                self.weapon_attribute[property_type] += value
            else:
                self.weapon_attribute[property_type] = value

    @abstractmethod
    async def check(self) -> bool: ...

    def get_attribute(self):
        promotion = None
        for equipment in EquipmentPromotionConfig:
            if equipment.EquipmentID == int(self.weapon_id):
                promotion = equipment
                break
        if not promotion:
            msg = f"EquipmentPromotionConfig not found: {self.weapon_id}"
            raise ValueError(msg)

        return BaseWeaponAttribute(
            hp=(
                promotion.BaseHP.Value
                + promotion.BaseHPAdd.Value * (self.weapon_level - 1)
            ),
            attack=(
                promotion.BaseAttack.Value
                + promotion.BaseAttackAdd.Value * (self.weapon_level - 1)
            ),
            defence=(
                promotion.BaseDefence.Value
                + promotion.BaseDefenceAdd.Value * (self.weapon_level - 1)
            ),
        )
