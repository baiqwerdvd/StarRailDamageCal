import copy
from typing import Dict

from ..damage.utils import merge_attribute


async def calculate_heal(
    base_attr: Dict[str, float],
    attribute_bonus: Dict[str, float],
    skill_type: str,
    skill_multiplier: float,
    skill_num: float,
    is_atk: int = 0,
):
    add_attr_bonus = copy.deepcopy(attribute_bonus)
    merged_attr = await merge_attribute(base_attr, add_attr_bonus)

    hp = merged_attr.get("attack", 0) if is_atk == 1 else merged_attr.get("hp", 0)

    # 检查是否有治疗量加成
    heal_ratio_base = merged_attr.get("HealRatioBase", 0)
    for attr in merged_attr:
        if "_HealRatioBase" in attr and attr.split("_")[0] in (skill_type):
            heal_ratio_base += merged_attr[attr]
    heal_ratio = heal_ratio_base + 1

    heal_num = (hp * skill_multiplier + skill_num) * heal_ratio

    return [heal_num]


async def calculate_shield(
    base_attr: Dict[str, float],
    attribute_bonus: Dict[str, float],
    skill_multiplier: float,
    skill_num: float,
    is_atk: int = 0,
):
    add_attr_bonus = copy.deepcopy(attribute_bonus)
    merged_attr = await merge_attribute(base_attr, add_attr_bonus)

    if is_atk == 1:
        defence = merged_attr.get("attack", 0)
    else:
        defence = merged_attr.get("defence", 0)

    # 检查是否有护盾加成
    shield_added_ratio = merged_attr.get("shield_added_ratio", 0)
    shield_added = shield_added_ratio + 1

    defence_num = (defence * skill_multiplier + skill_num) * shield_added

    return [defence_num]


async def get_damage(
    damege: int,
    base_attr: Dict[str, float],
    attribute_bonus: Dict[str, float],
    skill_type: str,
    add_skill_type: str,
    element: str,
    skill_multiplier: float,
):
    add_attr_bonus = copy.deepcopy(attribute_bonus)

    add_attr_bonus = apply_attribute_bonus(add_attr_bonus, skill_type, add_skill_type)

    merged_attr = await merge_attribute(base_attr, add_attr_bonus)

    injury_area = calculate_injury_area(
        merged_attr,
        skill_type,
        add_skill_type,
        element,
    )

    critical_damage = calculate_critical_damage(merged_attr, skill_type, add_skill_type)

    critical_chance = calculate_critical_chance(merged_attr, skill_type, add_skill_type)

    _ = calculate_expected_damage(critical_chance, critical_damage)

    damage_cd = damege * skill_multiplier * injury_area

    damage_qw = damege * skill_multiplier * injury_area

    damage_tz = damege * skill_multiplier * (injury_area + 2.626) * 10

    return [damage_cd, damage_qw, damage_tz]


async def break_damage(
    base_attr: Dict[str, float],
    attribute_bonus: Dict[str, float],
    skill_type: str,
    add_skill_type: str,
    element: str,
    level: int,
):
    break_element = {
        "Ice": 1,
        "Imaginary": 1,
        "Quantum": 1,
        "Thunder": 2,
        "Wind": 3,
        "Physical": 4,
        "Fire": 5,
    }

    add_attr_bonus = copy.deepcopy(attribute_bonus)

    add_attr_bonus = apply_attribute_bonus(add_attr_bonus, skill_type, add_skill_type)

    merged_attr = await merge_attribute(base_attr, add_attr_bonus)

    break_atk = 3767.55  # 80级敌人击破伤害基数, 我也不知道为什么是这个, 反正都说是这个

    damage_reduction = calculate_damage_reduction(level)

    resistance_area = calculate_resistance_area(
        merged_attr,
        skill_type,
        add_skill_type,
        element,
    )

    defence_multiplier = calculate_defence_multiplier(
        level, merged_attr, skill_type, add_skill_type
    )

    damage_ratio = calculate_damage_ratio(merged_attr, skill_type, add_skill_type)

    break_damage = merged_attr.get("BreakDamageAddedRatioBase", 0) + 1

    damage_cd = (
        break_atk
        * break_element[element]
        * 10
        * break_damage
        * damage_ratio
        * damage_reduction
        * resistance_area
        * defence_multiplier
    )

    return [damage_cd]


async def calculate_damage(
    base_attr: Dict[str, float],
    attribute_bonus: Dict[str, float],
    skill_type: str,
    add_skill_type: str,
    element: str,
    skill_multiplier: float,
    level: int,
    is_hp: int=0,
):
    add_attr_bonus = copy.deepcopy(attribute_bonus)

    add_attr_bonus = apply_attribute_bonus(add_attr_bonus, skill_type, add_skill_type)

    merged_attr = await merge_attribute(base_attr, add_attr_bonus)

    if is_hp == 1:
        attack = merged_attr.get("hp", 0)
    elif is_hp == 2:
        attack = merged_attr.get("defence", 0)
    else:
        attack = merged_attr.get("attack", 0)
    # print(f'攻击区:{attack}')
    damage_reduction = calculate_damage_reduction(level)
    # print(f'韧性区:{damage_reduction}')
    resistance_area = calculate_resistance_area(
        merged_attr,
        skill_type,
        add_skill_type,
        element,
    )
    # print(f'抗性区:{resistance_area}')
    defence_multiplier = calculate_defence_multiplier(
        level, merged_attr, skill_type, add_skill_type
    )
    # print(f'防御区:{defence_multiplier}')
    injury_area = calculate_injury_area(
        merged_attr,
        skill_type,
        add_skill_type,
        element,
    )
    # print(f'增伤区:{injury_area}')
    damage_ratio = calculate_damage_ratio(merged_attr, skill_type, add_skill_type)
    # print(f'易伤区:{damage_ratio}')
    critical_damage = calculate_critical_damage(merged_attr, skill_type, add_skill_type)
    # print(f'爆伤区:{critical_damage}')
    critical_chance = calculate_critical_chance(merged_attr, skill_type, add_skill_type)
    # print(f'暴击区:{critical_chance}')
    expected_damage = calculate_expected_damage(critical_chance, critical_damage)
    # print(f'期望区:{expected_damage}')
    damage_cd = calculate_damage_cd(
        attack,
        skill_multiplier,
        damage_ratio,
        injury_area,
        defence_multiplier,
        resistance_area,
        damage_reduction,
        critical_damage,
    )
    damage_qw = calculate_damage_qw(
        attack,
        skill_multiplier,
        damage_ratio,
        injury_area,
        defence_multiplier,
        resistance_area,
        damage_reduction,
        expected_damage,
    )

    damage_tz = await calculate_damage_tz(
        skill_multiplier,
        damage_ratio,
        damage_reduction,
        base_attr,
        add_attr_bonus,
        skill_type,
        add_skill_type,
        element,
        is_hp,
    )

    return [damage_cd, damage_qw, damage_tz]


def apply_attribute_bonus(
    add_attr_bonus: Dict[str, float],
    skill_type: str,
    add_skill_type: str,
):
    # Apply attribute bonuses to attack and status probability
    for attr in add_attr_bonus:
        if "AttackAddedRatio" in attr and attr.split("AttackAddedRatio")[0] in (
            skill_type,
            add_skill_type,
        ):
            # print(f'{attr} 有 {merged_attr[attr]} 攻击加成')
            add_attr_bonus["AttackAddedRatio"] += add_attr_bonus[attr]
        if "StatusProbabilityBase" in attr and attr.split("StatusProbabilityBase")[
            0
        ] in (skill_type, add_skill_type):
            add_attr_bonus["StatusProbabilityBase"] += add_attr_bonus[attr]
    return add_attr_bonus


def calculate_damage_reduction(level: int):
    _ = level
    enemy_damage_reduction = 0.1
    return 1 - enemy_damage_reduction


def calculate_resistance_area(
    merged_attr: Dict[str, float],
    skill_type: str,
    add_skill_type: str,
    element: str,
):
    _ = skill_type
    enemy_status_resistance = 0.0
    for attr in merged_attr:
        if "ResistancePenetration" in attr:
            # 检查是否有某一属性的抗性穿透
            attr_name = attr.split("ResistancePenetration")[0]
            if attr_name in (element, "AllDamage"):
                # print(f'{attr_name}属性有{merged_attr[attr]}穿透加成')
                enemy_status_resistance += merged_attr[attr]
            # 检查是否有某一技能属性的抗性穿透
            if "_" in attr_name:
                skill_name = attr_name.split("_")[0]
                skillattr_name = attr_name.split("_")[1]
                if skill_name == add_skill_type and skillattr_name in (
                    element,
                    "AllDamage",
                ):
                    enemy_status_resistance += merged_attr[attr]
                    # print(f'{skill_name}对{skillattr_name}属性有{merged_attr[attr]}穿透加成')
    return 1.0 - (0 - enemy_status_resistance)


def calculate_defence_multiplier(
    level: int,
    merged_attr: Dict[str, float],
    skill_type: str,
    add_skill_type: str,
):
    ignore_defence = merged_attr.get("ignore_defence", 0.0)
    for attr in merged_attr:
        skill_name = attr.split("ignore_defence")[0]
        if "ignore_defence" in attr and skill_name in (
            skill_type,
            add_skill_type,
        ):
            ignore_defence += merged_attr[attr]
    enemy_defence = (level * 10 + 200) * (1 - ignore_defence)
    return (level * 10 + 200) / (level * 10 + 200 + enemy_defence)


def calculate_injury_area(
    merged_attr: Dict[str, float],
    skill_type: str,
    add_skill_type: str,
    element: str,
):
    injury_area = 0.0
    for attr in merged_attr:
        attr_name = attr.split("AddedRatio")[0]
        skill_name = attr.split("DmgAdd")[0]
        if "DmgAdd" in attr and skill_name in (
            skill_type,
            add_skill_type,
        ):
            # print(f'{attr} 对 {skill_type} 有 {merged_attr[attr]} 伤害加成')
            injury_area += merged_attr[attr]

        if "AddedRatio" in attr and attr_name in (
            element,
            "AllDamage",
        ):
            # print(f'{attr} 对 {element} 属性有 {merged_attr[attr]} 伤害加成')
            injury_area += merged_attr[attr]
    return injury_area + 1


def calculate_damage_ratio(
    merged_attr: Dict[str, float],
    skill_type: str,
    add_skill_type: str,
):
    damage_ratio = merged_attr.get("DmgRatio", 0)
    for attr in merged_attr:
        if "_DmgRatio" in attr and attr.split("_")[0] in (
            skill_type,
            add_skill_type,
        ):
            damage_ratio += merged_attr[attr]
    return damage_ratio + 1


def calculate_critical_damage(
    merged_attr: Dict[str, float],
    skill_type: str,
    add_skill_type: str,
):
    if skill_type == "DOT":
        return 1.0
    critical_damage_base = merged_attr.get("CriticalDamageBase", 0)
    for attr in merged_attr:
        if "_CriticalDamageBase" in attr and attr.split("_")[0] in (
            skill_type,
            add_skill_type,
        ):
            # print(f'{attr} 有 {merged_attr[attr]} 爆伤加成')
            critical_damage_base += merged_attr[attr]
    return critical_damage_base + 1


def calculate_critical_chance(
    merged_attr: Dict[str, float],
    skill_type: str,
    add_skill_type: str,
):
    critical_chance_base = merged_attr["CriticalChanceBase"]
    for attr in merged_attr:
        if "_CriticalChance" in attr and attr.split("_")[0] in (
            skill_type,
            add_skill_type,
        ):
            # print(f'{attr} 有 {merged_attr[attr]} 暴击加成')
            critical_chance_base += merged_attr[attr]
    return min(1, critical_chance_base)


def calculate_expected_damage(
    critical_chance_base: float,
    critical_damage_base: float,
):
    return critical_chance_base * (critical_damage_base - 1) + 1


def calculate_damage_cd(
    attack: float,
    skill_multiplier: float,
    damage_ratio: float,
    injury_area: float,
    defence_multiplier: float,
    resistance_area: float,
    damage_reduction: float,
    critical_damage: float,
):
    return (
        attack
        * skill_multiplier
        * damage_ratio
        * injury_area
        * defence_multiplier
        * resistance_area
        * damage_reduction
        * critical_damage
    )


def calculate_damage_qw(
    attack: float,
    skill_multiplier: float,
    damage_ratio: float,
    injury_area: float,
    defence_multiplier: float,
    resistance_area: float,
    damage_reduction: float,
    expected_damage: float,
):
    return (
        attack
        * skill_multiplier
        * damage_ratio
        * injury_area
        * defence_multiplier
        * resistance_area
        * damage_reduction
        * expected_damage
    )


async def calculate_damage_tz(
    skill_multiplier: float,
    damage_ratio: float,
    damage_reduction: float,
    base_attr: Dict[str, float],
    add_attr_bonus: Dict[str, float],
    skill_type: str,
    add_skill_type: str,
    element: str,
    is_hp:int=0,
):
    add_attr_bonus_tz = copy.deepcopy(add_attr_bonus)
    add_attr_bonus_tz["AttackAddedRatio"] = (
        add_attr_bonus_tz.get("AttackAddedRatio", 0) + 1.694
    )
    add_attr_bonus_tz["ignore_defence"] = (
        add_attr_bonus_tz.get("ignore_defence", 0) + 0.44
    )
    add_attr_bonus_tz["AllDamageResistancePenetration"] = (
        add_attr_bonus_tz.get("AllDamageResistancePenetration", 0) + 0.27
    )
    add_attr_bonus_tz["AllDamageAddedRatio"] = (
        add_attr_bonus_tz.get("AllDamageAddedRatio", 0) + 2.06
    )
    add_attr_bonus_tz["CriticalDamageBase"] = (
        add_attr_bonus_tz.get("CriticalDamageBase", 0) + 4.578
    )
    merged_attr_tz = await merge_attribute(base_attr, add_attr_bonus_tz)
    if is_hp == 1:
        attack_tz = merged_attr_tz.get("hp", 0)
    elif is_hp == 2:
        attack_tz = merged_attr_tz.get("defence", 0)
    else:
        attack_tz = merged_attr_tz.get("attack", 0)

    resistance_area_tz = calculate_resistance_area(
        merged_attr_tz,
        skill_type,
        add_skill_type,
        element,
    )
    # print(f'抗性区:{resistance_area_tz}')
    defence_multiplier_tz = calculate_defence_multiplier(
        80, merged_attr_tz, skill_type, add_skill_type
    )
    # print(f'防御区:{defence_multiplier_tz}')
    injury_area_tz = calculate_injury_area(
        merged_attr_tz,
        skill_type,
        add_skill_type,
        element,
    )
    # print(f'增伤区:{injury_area_tz}')
    critical_damage_tz = calculate_critical_damage(
        merged_attr_tz, skill_type, add_skill_type
    )
    # print(f'爆伤区:{critical_damage_tz}')

    return (
        attack_tz
        * skill_multiplier
        * damage_ratio
        * injury_area_tz
        * defence_multiplier_tz
        * resistance_area_tz
        * damage_reduction
        * critical_damage_tz
        * 10
    )
