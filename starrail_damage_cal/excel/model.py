import json
from pathlib import Path
from typing import Dict, List, Union

from msgspec import Struct, convert

EXCEL = Path(__file__).parent


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


class SingleAvatarRelicScore(Struct):
    role: str
    HPDelta: float
    HPAddedRatio: float
    AttackDelta: float
    AttackAddedRatio: float
    DefenceDelta: float
    DefenceAddedRatio: float
    SpeedDelta: float
    CriticalChanceBase: float
    CriticalDamageBase: float
    BreakDamageAddedRatioBase: float
    HealRatio: float
    SPRatio: float
    StatusProbabilityBase: float
    StatusResistanceBase: float
    AttributeAddedRatio: float


with Path.open(EXCEL / "RelicMainAffixConfig.json", encoding="utf8") as f:
    RelicMainAffixConfig = convert(json.load(f), List[SingleRelicMainAffix])

with Path.open(EXCEL / "RelicSubAffixConfig.json", encoding="utf8") as f:
    RelicSubAffixConfig = convert(json.load(f), List[SingleRelicSubAffix])

with Path.open(EXCEL / "AvatarPromotionConfig.json", encoding="utf8") as f:
    AvatarPromotionConfig = convert(json.load(f), List[SingleAvatarPromotion])

with Path.open(EXCEL / "EquipmentPromotionConfig.json", encoding="utf8") as f:
    EquipmentPromotionConfig = convert(json.load(f), List[SingleEquipmentPromotion])

with Path.open(EXCEL / "AvatarRelicScore.json", encoding="utf8") as f:
    AvatarRelicScore = convert(json.load(f), List[SingleAvatarRelicScore])

with Path.open(EXCEL / "char_alias.json", encoding="utf8") as f:
    CharAlias = convert(json.load(f), Dict[str, Dict[str, List[str]]])
