import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from msgspec import json as msgjson

from starrail_damage_cal.damage.utils import cal_relic_main_affix, cal_relic_sub_affix
from starrail_damage_cal.excel.model import (
    AvatarPromotionConfig,
    EquipmentPromotionConfig,
)
from starrail_damage_cal.exception import (
    CharacterShowcaseNotOpenError,
)
from starrail_damage_cal.map.SR_MAP_PATH import (
    AvatarRankSkillUp,
    EquipmentID2Name,
    EquipmentID2Rarity,
    ItemId2Name,
    Property2Name,
    RelicId2SetId,
    SetId2Name,
    avatarId2DamageType,
    avatarId2EnName,
    avatarId2Name,
    avatarId2Rarity,
    characterSkillTree,
    rankId2Name,
    skillId2AttackType,
    skillId2Effect,
    skillId2Name,
)
from starrail_damage_cal.mihomo.models import Avatar, MihomoData
from starrail_damage_cal.mihomo.requests import get_char_card_info


async def api_to_model(
    uid: Union[str, None] = None,
    mihomo_raw: Union[MihomoData, None] = None,
    save_path: Union[Path, None] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    pass


async def api_to_dict(
    uid: Union[str, None] = None,
    mihomo_raw: Union[MihomoData, None] = None,
    save_path: Union[Path, None] = None,
) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
    if not mihomo_raw:
        if not uid:
            raise KeyError
        sr_data = await get_char_card_info(uid)
    else:
        sr_data = mihomo_raw

    PlayerDetailInfo = sr_data.detailInfo

    if save_path and uid:
        path = save_path / uid
        path.mkdir(parents=True, exist_ok=True)
        with Path.open(path / f"{uid!s}.json", "wb") as file:
            _ = file.write(msgjson.format(msgjson.encode(PlayerDetailInfo), indent=4))
        with Path.open(path / "rawData.json", "wb") as file:
            _ = file.write(msgjson.format(msgjson.encode(sr_data), indent=4))

    player_uid = str(PlayerDetailInfo.uid)

    char_name_list: List[str] = []
    char_id_list: List[str] = []
    char_data_list: Dict[str, Dict] = {}
    nickName = PlayerDetailInfo.nickname
    avatarList = (
        PlayerDetailInfo.avatarDetailList if PlayerDetailInfo.avatarDetailList else []
    ) + (PlayerDetailInfo.assistAvatarList if PlayerDetailInfo.assistAvatarList else [])
    for char in avatarList:
        if str(char.avatarId) in char_id_list:
            continue
        char_data, avatarName = await get_data(
            char,
            nickName,
            player_uid,
            save_path,
        )
        char_name_list.append(avatarName)
        char_id_list.append(str(char.avatarId))
        char_data_list[str(char.avatarId)] = char_data

    if not char_name_list:
        raise CharacterShowcaseNotOpenError(player_uid)

    return (char_id_list, char_data_list)


async def get_data(
    char: Avatar, nick_name: str, uid: str, save_path: Union[Path, None] = None
):
    # 处理基本信息
    char_data = {
        "uid": uid,
        "nickName": nick_name,
        "avatarId": char.avatarId,
        "avatarName": avatarId2Name[str(char.avatarId)],
        "avatarElement": avatarId2DamageType[str(char.avatarId)],
        "avatarRarity": avatarId2Rarity[str(char.avatarId)],
        "avatarPromotion": char.promotion,
        "avatarLevel": char.level,
        "avatarSkill": [],
        "avatarExtraAbility": [],
        "avatarAttributeBonus": [],
        "RelicInfo": [],
    }
    avatarName = avatarId2Name[str(char.avatarId)]
    char_data["avatarEnName"] = avatarId2EnName[str(char.avatarId)]
    # 处理技能
    for behavior in char.skillTreeList:
        # 处理技能
        if f"{char.avatarId}0" == str(behavior.pointId)[0:5]:
            skill_temp = {}
            skill_temp["skillId"] = char.avatarId * 100 + behavior.pointId % 10
            skill_temp["skillName"] = skillId2Name[str(skill_temp["skillId"])]
            skill_temp["skillEffect"] = skillId2Effect[str(skill_temp["skillId"])]
            skill_temp["skillAttackType"] = skillId2AttackType[
                str(skill_temp["skillId"])
            ]
            skill_temp["skillLevel"] = behavior.level
            char_data["avatarSkill"].append(skill_temp)

        # 处理技能树中的额外能力
        if f"{char.avatarId}1" == str(behavior.pointId)[0:5]:
            extra_ability_temp = {}
            extra_ability_temp["extraAbilityId"] = behavior.pointId
            extra_ability_temp["extraAbilityLevel"] = behavior.level
            char_data["avatarExtraAbility"].append(extra_ability_temp)

        # 处理技能树中的属性加成
        if f"{char.avatarId}2" == str(behavior.pointId)[0:5]:
            attribute_bonus_temp = {}
            attribute_bonus_temp["attributeBonusId"] = behavior.pointId
            attribute_bonus_temp["attributeBonusLevel"] = behavior.level
            status_add = characterSkillTree[str(char.avatarId)][str(behavior.pointId)][
                "levels"
            ][behavior.level - 1]["properties"]
            attribute_bonus_temp["statusAdd"] = {}
            if status_add:
                for property_ in status_add:
                    attribute_bonus_temp["statusAdd"]["property"] = property_["type"]
                    attribute_bonus_temp["statusAdd"]["name"] = Property2Name[
                        property_["type"]
                    ]
                    attribute_bonus_temp["statusAdd"]["value"] = property_["value"]
                    char_data["avatarAttributeBonus"].append(attribute_bonus_temp)

    # 处理遗器
    if char.relicList:
        for relic in char.relicList:
            relic_temp = {}
            relic_temp["relicId"] = relic.tid
            relic_temp["relicName"] = ItemId2Name[str(relic.tid)]
            relic_temp["SetId"] = int(RelicId2SetId[str(relic.tid)])
            relic_temp["SetName"] = SetId2Name[str(relic_temp["SetId"])]
            relic_temp["Level"] = relic.level if relic.level else 0
            relic_temp["Type"] = relic.type_

            relic_temp["MainAffix"] = {}
            relic_temp["MainAffix"]["AffixID"] = relic.mainAffixId
            affix_property, value = await cal_relic_main_affix(
                relic_id=relic.tid,
                set_id=str(relic_temp["SetId"]),
                affix_id=relic.mainAffixId,
                relic_type=relic.type_,
                relic_level=relic_temp["Level"],
            )
            relic_temp["MainAffix"]["Property"] = affix_property
            relic_temp["MainAffix"]["Name"] = Property2Name[affix_property]
            relic_temp["MainAffix"]["Value"] = value

            relic_temp["SubAffixList"] = []
            if relic.subAffixList:
                for sub_affix in relic.subAffixList:
                    sub_affix_temp = {}
                    sub_affix_temp["SubAffixID"] = sub_affix.affixId
                    sub_affix_property, value = await cal_relic_sub_affix(
                        relic_id=relic.tid,
                        affix_id=sub_affix.affixId,
                        cnt=sub_affix.cnt,
                        step=sub_affix.step if sub_affix.step else 0,
                    )
                    sub_affix_temp["Property"] = sub_affix_property
                    sub_affix_temp["Name"] = Property2Name[sub_affix_property]
                    sub_affix_temp["Cnt"] = sub_affix.cnt
                    sub_affix_temp["Step"] = sub_affix.step if sub_affix.step else 0
                    sub_affix_temp["Value"] = value
                    relic_temp["SubAffixList"].append(sub_affix_temp)
            char_data["RelicInfo"].append(relic_temp)

    # 处理命座
    rank_temp = []
    if char.rank and char.rank is not None:
        char_data["rank"] = char.rank
        for index in range(char.rank):
            rankTemp = {}
            rank_id = int(str(char.avatarId) + "0" + str(index + 1))
            rankTemp["rankId"] = rank_id
            rankTemp["rankName"] = rankId2Name[str(rank_id)]
            rank_temp.append(rankTemp)
        char_data["rankList"] = rank_temp

    # 处理命座中的 level_up_skills
    if char_data.get("rankList"):
        for rank_item in char_data["rankList"]:
            rank_id = rank_item["rankId"]
            level_up_skill = AvatarRankSkillUp[str(rank_id)]
            if level_up_skill:
                for item in level_up_skill:
                    skill_id = item["id"]
                    skill_up_num = item["num"]
                    # 查找skill_id在不在avatarSkill中
                    for index, skill_item in enumerate(char_data["avatarSkill"]):
                        if str(skill_id) == str(skill_item["skillId"]):
                            char_data["avatarSkill"][index]["skillLevel"] += (
                                skill_up_num
                            )
                            break

    # 处理基础属性
    base_attributes = {}
    avatar_promotion_base = None
    for avatar in AvatarPromotionConfig:
        if avatar.AvatarID == char.avatarId and avatar.Promotion == char.promotion:
            avatar_promotion_base = avatar
            break
    if not avatar_promotion_base:
        msg = f"AvatarPromotionConfig not found: {char.avatarId}"
        raise ValueError(msg)

    # 攻击力
    base_attributes["attack"] = (
        avatar_promotion_base.AttackBase.Value
        + avatar_promotion_base.AttackAdd.Value * (char.level - 1)
    )
    # 防御力
    base_attributes["defence"] = (
        avatar_promotion_base.DefenceBase.Value
        + avatar_promotion_base.DefenceAdd.Value * (char.level - 1)
    )
    # 血量
    base_attributes["hp"] = (
        avatar_promotion_base.HPBase.Value
        + avatar_promotion_base.HPAdd.Value * (char.level - 1)
    )
    # 速度
    base_attributes["speed"] = avatar_promotion_base.SpeedBase.Value
    # 暴击率
    base_attributes["CriticalChanceBase"] = avatar_promotion_base.CriticalChance.Value
    # 暴击伤害
    base_attributes["CriticalDamageBase"] = avatar_promotion_base.CriticalDamage.Value
    # 嘲讽
    base_attributes["BaseAggro"] = avatar_promotion_base.BaseAggro.Value

    char_data["baseAttributes"] = base_attributes

    # 处理武器
    equipment_info = {}
    if char.equipment and char.equipment.tid is not None:
        equipment_info["equipmentID"] = char.equipment.tid
        equipment_info["equipmentName"] = EquipmentID2Name[str(char.equipment.tid)]

        equipment_info["equipmentLevel"] = char.equipment.level
        equipment_info["equipmentPromotion"] = char.equipment.promotion
        equipment_info["equipmentRank"] = char.equipment.rank
        equipment_info["equipmentRarity"] = EquipmentID2Rarity[str(char.equipment.tid)]
        equipment_base_attributes = {}
        equipment_promotion_base = None
        for equipment in EquipmentPromotionConfig:
            if equipment.EquipmentID == char.equipment.tid and equipment.Promotion == char.equipment.promotion:
                equipment_promotion_base = equipment
                break
        if not equipment_promotion_base:
            msg = f"EquipmentPromotionConfig not found: {char.equipment.tid}"
            raise ValueError(msg)

        equipment_level = char.equipment.level if char.equipment.level else 1
        # 生命值
        equipment_base_attributes["hp"] = (
            equipment_promotion_base.BaseHP.Value
            + equipment_promotion_base.BaseHPAdd.Value * (equipment_level - 1)
        )
        # 攻击力
        equipment_base_attributes["attack"] = (
            equipment_promotion_base.BaseAttack.Value
            + equipment_promotion_base.BaseAttackAdd.Value * (equipment_level - 1)
        )
        # 防御力
        equipment_base_attributes["defence"] = (
            equipment_promotion_base.BaseDefence.Value
            + equipment_promotion_base.BaseDefenceAdd.Value * (equipment_level - 1)
        )
        equipment_info["baseAttributes"] = equipment_base_attributes

    char_data["equipmentInfo"] = equipment_info

    if save_path:
        path = save_path / str(uid)
        path.mkdir(parents=True, exist_ok=True)
        path.mkdir(parents=True, exist_ok=True)
        with Path.open(path / f"{avatarName}.json", "w", encoding="UTF-8") as file:
            json.dump(char_data, file, ensure_ascii=False)

    return char_data, avatarName
