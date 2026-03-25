from pathlib import Path
from typing import Dict, List, TypedDict, Union

from msgspec import Struct
from msgspec import json as msgjson

from .. import data_paths
from ..version import StarRail_version

MAP = Path(__file__).parent / "data"

version = StarRail_version

avatarId2Name_fileName = f"avatarId2Name_mapping.json"
avatarId2EnName_fileName = f"avatarId2EnName_mapping.json"
EquipmentID2Name_fileName = f"EquipmentID2Name_mapping.json"
EquipmentID2EnName_fileName = f"EquipmentID2EnName_mapping.json"
skillId2Name_fileName = f"skillId2Name_mapping.json"
skillId2Type_fileName = f"skillId2Type_mapping.json"
Property2Name_fileName = f"Property2Name_mapping.json"
RelicId2SetId_fileName = f"RelicId2SetId_mapping.json"
SetId2Name_fileName = f"SetId2Name_mapping.json"
rankId2Name_fileName = f"rankId2Name_mapping.json"
characterSkillTree_fileName = f"characterSkillTree_mapping.json"
avatarId2DamageType_fileName = f"avatarId2DamageType_mapping.json"
avatarId2Rarity_fileName = f"avatarId2Rarity_mapping.json"
EquipmentID2AbilityProperty_fileName = f"EquipmentID2AbilityProperty_mapping.json"
RelicSetSkill_fileName = f"RelicSetSkill_mapping.json"
skillId2AttackType_fileName = f"skillId2AttackType_mapping.json"
EquipmentID2Rarity_fileName = f"EquipmentID2Rarity_mapping.json"
RelicId2Rarity_fileName = f"RelicId2Rarity_mapping.json"
ItemId2Name_fileName = f"ItemId2Name_mapping.json"
RelicId2MainAffixGroup_fileName = f"RelicId2MainAffixGroup_mapping.json"
avatarRankSkillUp_fileName = f"avatarRankSkillUp_mapping.json"
MysPropertyType2Property_fileName = "MysPropertyType2Property_mapping.json"


class TS(TypedDict):
    Name: Dict[str, str]
    Icon: Dict[str, str]


class LU(Struct):
    id: str
    num: int


class TV(Struct):
    type: str
    value: float


class AbilityPropertyValue(Struct):
    Value: float


class AbilityProperty(Struct):
    PropertyType: str
    Value: AbilityPropertyValue


class SkillTreeLevel(Struct):
    promotion: int
    level: int
    properties: List[TV]
    materials: List[LU]


class CharacterSkillTreeModel(Struct):
    id: str
    name: str
    max_level: int
    desc: str
    params: List[List[float]]
    anchor: str
    pre_points: List[str]
    level_up_skills: List[LU]
    levels: List[SkillTreeLevel]
    icon: str


class RelicSetStatusAdd(Struct):
    Property: str
    Value: float


def _load_map_json(file_name: str, data_type):
    with Path.open(
        data_paths.resolve_data_path(Path("map") / "data" / file_name),
        encoding="UTF-8",
    ) as f:
        return msgjson.decode(f.read(), type=data_type)


def _replace_dict(name: str, values: dict) -> None:
    current_value = globals().get(name)
    if isinstance(current_value, dict):
        current_value.clear()
        current_value.update(values)
        return
    globals()[name] = values


def reload_map_data() -> None:
    _replace_dict(
        "avatarId2Name",
        _load_map_json(avatarId2Name_fileName, Dict[str, str]),
    )
    _replace_dict(
        "avatarId2EnName",
        _load_map_json(avatarId2EnName_fileName, Dict[str, str]),
    )
    _replace_dict(
        "EquipmentID2Name",
        _load_map_json(EquipmentID2Name_fileName, Dict[str, str]),
    )
    _replace_dict(
        "EquipmentID2EnName",
        _load_map_json(EquipmentID2EnName_fileName, Dict[str, str]),
    )
    _replace_dict(
        "skillId2Name",
        _load_map_json(skillId2Name_fileName, Dict[str, str]),
    )
    _replace_dict(
        "skillId2Effect",
        _load_map_json(skillId2Type_fileName, Dict[str, str]),
    )
    _replace_dict(
        "Property2Name",
        _load_map_json(Property2Name_fileName, Dict[str, str]),
    )
    _replace_dict(
        "RelicId2SetId",
        _load_map_json(RelicId2SetId_fileName, Dict[str, int]),
    )
    _replace_dict(
        "SetId2Name",
        _load_map_json(SetId2Name_fileName, Dict[str, str]),
    )
    _replace_dict(
        "rankId2Name",
        _load_map_json(rankId2Name_fileName, Dict[str, str]),
    )
    _replace_dict(
        "characterSkillTree",
        _load_map_json(
            characterSkillTree_fileName,
            Dict[str, Dict[str, CharacterSkillTreeModel]],
        ),
    )
    _replace_dict(
        "avatarId2DamageType",
        _load_map_json(avatarId2DamageType_fileName, Dict[str, str]),
    )
    _replace_dict(
        "avatarId2Rarity",
        _load_map_json(avatarId2Rarity_fileName, Dict[str, str]),
    )
    _replace_dict(
        "EquipmentID2AbilityProperty",
        _load_map_json(
            EquipmentID2AbilityProperty_fileName,
            Dict[str, Dict[str, List[AbilityProperty]]],
        ),
    )
    _replace_dict(
        "RelicSetSkill",
        _load_map_json(
            RelicSetSkill_fileName,
            Dict[str, Dict[str, RelicSetStatusAdd]],
        ),
    )
    _replace_dict(
        "skillId2AttackType",
        _load_map_json(skillId2AttackType_fileName, Dict[str, str]),
    )
    _replace_dict(
        "EquipmentID2Rarity",
        _load_map_json(EquipmentID2Rarity_fileName, Dict[str, int]),
    )
    _replace_dict(
        "ItemId2Name",
        _load_map_json(ItemId2Name_fileName, Dict[str, str]),
    )
    _replace_dict(
        "RelicId2MainAffixGroup",
        _load_map_json(RelicId2MainAffixGroup_fileName, Dict[str, int]),
    )
    _replace_dict(
        "AvatarRankSkillUp",
        _load_map_json(avatarRankSkillUp_fileName, Dict[str, Union[List[LU], None]]),
    )
    _replace_dict(
        "RelicId2Rarity",
        _load_map_json(RelicId2Rarity_fileName, Dict[str, int]),
    )
    _replace_dict(
        "MysPropertyType2Property",
        _load_map_json(MysPropertyType2Property_fileName, Dict[str, str]),
    )


reload_map_data()
