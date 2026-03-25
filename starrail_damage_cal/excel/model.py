import json
from pathlib import Path
from typing import Dict, List, Union

from msgspec import Struct, convert, field

from .. import data_paths

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
    Promotion: int = 0
    PlayerLevelRequire: Union[int, None] = None


class SingleRelicMainAffix(Struct):
    GroupID: int
    AffixID: int
    Property: str
    BaseValue: PromotionAttr
    LevelAdd: PromotionAttr
    IsAvailable: Union[bool, None] = None


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


class SingleStarRailRelicMain(Struct):
    HPDelta: Union[float, None] = None
    AttackDelta: Union[float, None] = None
    HPAddedRatio: Union[float, None] = None
    AttackAddedRatio: Union[float, None] = None
    DefenceAddedRatio: Union[float, None] = None
    CriticalDamageBase: Union[float, None] = None
    CriticalChanceBase: Union[float, None] = None
    HealRatioBase: Union[float, None] = None
    StatusProbabilityBase: Union[float, None] = None
    SpeedDelta: Union[float, None] = None
    PhysicalAddedRatio: Union[float, None] = None
    FireAddedRatio: Union[float, None] = None
    IceAddedRatio: Union[float, None] = None
    ThunderAddedRatio: Union[float, None] = None
    WindAddedRatio: Union[float, None] = None
    QuantumAddedRatio: Union[float, None] = None
    ImaginaryAddedRatio: Union[float, None] = None
    BreakDamageAddedRatioBase: Union[float, None] = None
    SPRatioBase: Union[float, None] = None


class SingleStarRailRelicWeight(Struct):
    HPDelta: float
    AttackDelta: float
    DefenceDelta: float
    HPAddedRatio: float
    AttackAddedRatio: float
    DefenceAddedRatio: float
    SpeedDelta: float
    CriticalChanceBase: float
    CriticalDamageBase: float
    StatusProbabilityBase: float
    StatusResistanceBase: float
    BreakDamageAddedRatioBase: float


class SingleStarRailRelicScore(Struct):
    main: Dict[str, SingleStarRailRelicMain]
    weight: SingleStarRailRelicWeight
    max_value: float = field(name="max")


def _load_excel_json(file_name: str):
    with Path.open(
        data_paths.resolve_data_path(Path("excel") / file_name),
        encoding="utf8",
    ) as f:
        return json.load(f)


def _replace_list(name: str, values: list) -> None:
    current_value = globals().get(name)
    if isinstance(current_value, list):
        current_value[:] = values
        return
    globals()[name] = values


def _replace_dict(name: str, values: dict) -> None:
    current_value = globals().get(name)
    if isinstance(current_value, dict):
        current_value.clear()
        current_value.update(values)
        return
    globals()[name] = values


def reload_excel_data() -> None:
    _replace_list(
        "RelicMainAffixConfig",
        convert(
            _load_excel_json("RelicMainAffixConfig.json"), List[SingleRelicMainAffix]
        ),
    )
    _replace_list(
        "RelicSubAffixConfig",
        convert(
            _load_excel_json("RelicSubAffixConfig.json"), List[SingleRelicSubAffix]
        ),
    )

    avatar_promotion = convert(
        _load_excel_json("AvatarPromotionConfig.json"),
        List[SingleAvatarPromotion],
    )
    avatar_promotion += convert(
        _load_excel_json("AvatarPromotionConfigLD.json"),
        List[SingleAvatarPromotion],
    )
    _replace_list("AvatarPromotionConfig", avatar_promotion)

    _replace_list(
        "EquipmentPromotionConfig",
        convert(
            _load_excel_json("EquipmentPromotionConfig.json"),
            List[SingleEquipmentPromotion],
        ),
    )
    _replace_list(
        "AvatarRelicScore",
        convert(
            _load_excel_json("AvatarRelicScore.json"), List[SingleAvatarRelicScore]
        ),
    )
    _replace_dict(
        "CharAlias",
        convert(_load_excel_json("char_alias.json"), Dict[str, Dict[str, List[str]]]),
    )
    _replace_dict(
        "StarRailRelicScores",
        convert(
            _load_excel_json("relic_scores.json"),
            Dict[str, SingleStarRailRelicScore],
        ),
    )


reload_excel_data()
