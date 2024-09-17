from typing import Dict

from ..excel.model import RelicMainAffixConfig, RelicSubAffixConfig
from ..map.SR_MAP_PATH import RelicId2MainAffixGroup


async def cal_relic_main_affix(
    relic_id: int,
    set_id: str,
    affix_id: int,
    relic_type: int,
    relic_level: int,
):
    if set_id[0] == "3":
        rarity = int(str(relic_id)[0]) - 1
        group_id = str(rarity) + str(relic_type)
    else:
        group_id = str(RelicId2MainAffixGroup[str(relic_id)])
    relic_data = None
    for relic in RelicMainAffixConfig:
        if relic.GroupID == int(group_id) and relic.AffixID == affix_id:
            relic_data = relic
            break
    if relic_data is None:
        msg = f"RelicMainAffixConfig not found: {group_id} {affix_id}"
        raise ValueError(msg)
    base_value = relic_data.BaseValue.Value
    level_add = relic_data.LevelAdd.Value
    value = base_value + level_add * relic_level
    affix_property = relic_data.Property
    return affix_property, value


async def cal_relic_sub_affix(relic_id: int, affix_id: int, cnt: int, step: int):
    rarity = int(str(relic_id)[0]) - 1
    relic_data = None
    for relic in RelicSubAffixConfig:
        if relic.AffixID == affix_id and relic.GroupID == rarity:
            relic_data = relic
            break
    if relic_data is None:
        msg = f"RelicSubAffixConfig not found: {rarity} {affix_id}"
        raise ValueError(msg)
    base_value = relic_data.BaseValue.Value
    step_value = relic_data.StepValue.Value
    value = base_value * cnt + step_value * step
    affix_property = relic_data.Property
    return affix_property, value


async def merge_attribute(
    base_attr: Dict[str, float],
    attribute_bonus: Dict[str, float],
) -> Dict[str, float]:
    merged_attr = base_attr.copy()
    for attribute, value in attribute_bonus.items():
        if attribute.endswith("Delta"):
            attr = attribute.split("Delta")[0].lower()
            if attr in merged_attr:
                merged_attr[attr] += value
            else:
                merged_attr[attribute] = attribute_bonus[attribute]
        elif attribute.endswith("AddedRatio"):
            attr = attribute.split("AddedRatio")[0].lower()
            if attr in merged_attr:
                merged_attr[attr] += base_attr[attr] * value
            else:
                merged_attr[attribute] = attribute_bonus[attribute]
        # elif attribute in [
        #     "ignore_defence",
        #     "Atk_buff",
        #     "Normal_buff",
        #     "shield_added_ratio",
        # ]:
        #     merged_attr[attribute] = base_attr.get(attribute, 0) + value
        elif attribute.endswith(
            ("ResistancePenetration", "DmgAdd", "DmgRatio", "Base"),
        ) or attribute in [
            "ignore_defence",
            "Atk_buff",
            "Normal_buff",
            "shield_added_ratio",
        ]:
            merged_attr[attribute] = base_attr.get(attribute, 0) + value
        # elif attribute.endswith("Base"):
        #     merged_attr[attribute] = base_attr.get(attribute, 0) + value
        else:
            merged_attr[attribute] = attribute_bonus[attribute]
    return merged_attr
