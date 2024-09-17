from typing import List, Union

from msgspec import Struct, convert

from starrail_damage_cal.excel.read_excel import (
    AvatarPromotion,
    EquipmentPromotion,
    RelicMainAffix,
    RelicSubAffix,
)


class PromotionCost(Struct):
    ItemID: int
    ItemNum: int


class PromotionAttr(Struct):
    Value: float


class SingleAvatarPromotion(Struct):
    AvatarID: int
    PromotionCostList: List[PromotionCost]
    MaxLevel: int
    # WorldLevelRequire: Union[int, None]
    AttackBase: PromotionAttr
    AttackAdd: PromotionAttr
    DefenceBase: PromotionAttr
    DefenceAdd: PromotionAttr
    HPBase: PromotionAttr
    HPAdd: PromotionAttr
    SpeedBase: PromotionAttr
    CriticalChance: PromotionAttr
    CriticalDamage: PromotionAttr
    BaseAggro: PromotionAttr
    Promotion: Union[int, None] = None
    PlayerLevelRequire: Union[int, None] = None


class SingleEquipmentPromotion(Struct):
    EquipmentID: int
    PromotionCostList: List[PromotionCost]
    MaxLevel: int
    # WorldLevelRequire: Union[int, None]
    BaseHP: PromotionAttr
    BaseHPAdd: PromotionAttr
    BaseAttack: PromotionAttr
    BaseAttackAdd: PromotionAttr
    BaseDefence: PromotionAttr
    BaseDefenceAdd: PromotionAttr
    Promotion: Union[int, None] = None
    PlayerLevelRequire: Union[int, None] = None


class SingleRelicMainAffix(Struct):
    GroupID: int
    AffixID: int
    Property: str
    BaseValue: PromotionAttr
    LevelAdd: PromotionAttr
    IsAvailable: bool


class SingleRelicSubAffix(Struct):
    GroupID: int
    AffixID: int
    Property: str
    BaseValue: PromotionAttr
    StepValue: PromotionAttr
    StepNum: int


AvatarPromotionConfig = convert(AvatarPromotion, List[SingleAvatarPromotion])
EquipmentPromotionConfig = convert(EquipmentPromotion, List[SingleEquipmentPromotion])
RelicMainAffixConfig = convert(RelicMainAffix, List[SingleRelicMainAffix])
RelicSubAffixConfig = convert(RelicSubAffix, List[SingleRelicSubAffix])
