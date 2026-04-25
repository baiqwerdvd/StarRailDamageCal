from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from msgspec import json as msgjson

from .damage.utils import cal_relic_main_affix, cal_relic_sub_affix
from .excel.model import (
    AvatarPromotionConfig,
    EquipmentPromotionConfig,
)
from .exception import (
    CharacterShowcaseNotOpenError,
)
from .map.SR_MAP_PATH import (
    AvatarRankSkillUp,
    EquipmentID2Name,
    EquipmentID2Rarity,
    ItemId2Name,
    MysPropertyType2Property,
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
from .mihomo.models import Avatar, MihomoData
from .mihomo.requests import get_char_card_info
from .model import (
    AttributeBounsStatusAdd,
    AvatarBaseAttributes,
    AvatarEquipmentInfo,
    EquipmentBaseAttributes,
    MihomoAvatarAttributeBonus,
    MihomoAvatarExtraAbility,
    MihomoAvatarSkill,
    MihomoCharacter,
    RankData,
    Relic,
    RelicMainAffix,
    RelicSubAffix,
)


async def api_to_dict(
    uid: Union[str, None] = None,
    mihomo_raw: Union[MihomoData, None] = None,
    save_path: Union[Path, None] = None,
) -> Tuple[List[str], Dict[str, MihomoCharacter]]:
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
    char_data_list: Dict[str, MihomoCharacter] = {}
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


def _normalize_promotion(promotion: Any) -> int:
    return int(promotion or 0)


def _get_avatar_promotion_config(avatar_id: int, promotion: Any):
    normalized_promotion = _normalize_promotion(promotion)
    for avatar in AvatarPromotionConfig:
        if (
            avatar.AvatarID == avatar_id
            and _normalize_promotion(avatar.Promotion) == normalized_promotion
        ):
            return avatar

    msg = f"AvatarPromotionConfig not found: {avatar_id}"
    raise ValueError(msg)


def _get_equipment_promotion_config(equipment_id: int, promotion: Any):
    normalized_promotion = _normalize_promotion(promotion)
    for equipment in EquipmentPromotionConfig:
        if (
            equipment.EquipmentID == equipment_id
            and _normalize_promotion(equipment.Promotion) == normalized_promotion
        ):
            return equipment

    msg = f"EquipmentPromotionConfig not found: {equipment_id}"
    raise ValueError(msg)


async def get_data(
    char: Avatar, nick_name: str, uid: str, save_path: Union[Path, None] = None
) -> Tuple[MihomoCharacter, str]:
    # 处理基本信息
    char_data = MihomoCharacter(
        uid=uid,
        nickName=nick_name,
        avatarId=char.avatarId,
        avatarName=avatarId2Name[str(char.avatarId)],
        avatarElement=avatarId2DamageType[str(char.avatarId)],
        avatarRarity=avatarId2Rarity[str(char.avatarId)],
        avatarPromotion=char.promotion if char.promotion else 0,
        avatarLevel=char.level,
        avatarSkill=[],
        avatarExtraAbility=[],
        avatarAttributeBonus=[],
        RelicInfo=[],
        avatarEnName=avatarId2EnName[str(char.avatarId)],
        baseAttributes=AvatarBaseAttributes(
            hp=0,
            attack=0,
            defence=0,
            speed=0,
            CriticalChanceBase=0,
            CriticalDamageBase=0,
            BaseAggro=0,
        ),
        equipmentInfo=AvatarEquipmentInfo(
            equipmentID=0,
            equipmentName="",
            equipmentLevel=0,
            equipmentPromotion=0,
            equipmentRank=0,
            equipmentRarity=0,
            baseAttributes=EquipmentBaseAttributes(hp=0, attack=0, defence=0),
        ),
        rank=0,
        rankList=[],
        enhancedId=char.enhancedId if char.enhancedId else 0,
    )
    # 处理技能
    for behavior in char.skillTreeList:
        # 处理技能
        if (
            f"{char.avatarId}0" == str(behavior.pointId)[0:5]
            or f"{char_data.enhancedId}{char.avatarId}0" == str(behavior.pointId)[0:6]
        ):
            skillId = (
                char.avatarId * 100
                + behavior.pointId % 10
                + char_data.enhancedId * 1000000
            )
            skill_temp = MihomoAvatarSkill(
                skillId=skillId,
                skillName=skillId2Name[str(skillId)],
                skillEffect=skillId2Effect[str(skillId)],
                skillAttackType=skillId2AttackType[str(skillId)],
                skillLevel=behavior.level,
            )
            char_data.avatarSkill.append(skill_temp)

        # 处理技能树中的额外能力
        if (
            f"{char.avatarId}1" == str(behavior.pointId)[0:5]
            or f"{char_data.enhancedId}{char.avatarId}1" == str(behavior.pointId)[0:6]
        ):
            extra_ability_temp = MihomoAvatarExtraAbility(
                extraAbilityId=behavior.pointId,
                extraAbilityLevel=behavior.level,
            )
            char_data.avatarExtraAbility.append(extra_ability_temp)

        # 处理技能树中的属性加成
        if (
            f"{char.avatarId}2" == str(behavior.pointId)[0:5]
            or f"{char_data.enhancedId}{char.avatarId}2" == str(behavior.pointId)[0:6]
        ):
            attribute_bonus_temp = MihomoAvatarAttributeBonus(
                attributeBonusId=behavior.pointId,
                attributeBonusLevel=behavior.level,
                statusAdd=AttributeBounsStatusAdd(
                    property_="",
                    name="",
                    value=0,
                ),
            )
            status_add = (
                characterSkillTree[str(char.avatarId)][str(behavior.pointId)]
                .levels[behavior.level - 1]
                .properties
            )
            # if status_add:
            for property_ in status_add:
                attribute_bonus_temp.statusAdd.property_ = property_.type
                attribute_bonus_temp.statusAdd.name = Property2Name[property_.type]
                attribute_bonus_temp.statusAdd.value = property_.value
                char_data.avatarAttributeBonus.append(attribute_bonus_temp)

    # 处理遗器
    if char.relicList:
        for relic in char.relicList:
            relic_temp = Relic(
                relicId=relic.tid,
                relicName=ItemId2Name[str(relic.tid)],
                SetId=RelicId2SetId[str(relic.tid)],
                SetName=SetId2Name[str(RelicId2SetId[str(relic.tid)])],
                Type=relic.type_,
                MainAffix=RelicMainAffix(
                    AffixID=0,
                    Property="",
                    Name="",
                    Value=0,
                ),
                SubAffixList=[],
                Level=relic.level if relic.level else 0,
            )

            relic_temp.MainAffix.AffixID = relic.mainAffixId
            affix_property, value = await cal_relic_main_affix(
                relic_id=relic.tid,
                set_id=str(relic_temp.SetId),
                affix_id=relic.mainAffixId,
                relic_type=relic.type_,
                relic_level=relic_temp.Level,
            )
            relic_temp.MainAffix.Property = affix_property
            relic_temp.MainAffix.Name = Property2Name[affix_property]
            relic_temp.MainAffix.Value = value

            if relic.subAffixList:
                for sub_affix in relic.subAffixList:
                    sub_affix_temp = RelicSubAffix(
                        SubAffixID=0,
                        Property="",
                        Name="",
                        Cnt=0,
                        Step=0,
                        Value=0,
                    )
                    sub_affix_temp.SubAffixID = sub_affix.affixId
                    sub_affix_property, value = await cal_relic_sub_affix(
                        relic_id=relic.tid,
                        affix_id=sub_affix.affixId,
                        cnt=sub_affix.cnt,
                        step=sub_affix.step if sub_affix.step else 0,
                    )
                    sub_affix_temp.Property = sub_affix_property
                    sub_affix_temp.Name = Property2Name[sub_affix_property]
                    sub_affix_temp.Cnt = sub_affix.cnt
                    sub_affix_temp.Step = sub_affix.step if sub_affix.step else 0
                    sub_affix_temp.Value = value
                    relic_temp.SubAffixList.append(sub_affix_temp)
            char_data.RelicInfo.append(relic_temp)

    # 处理命座
    rank_temp: List[RankData] = []
    if char.rank:
        char_data.rank = char.rank
        for index in range(char.rank):
            rankTemp = RankData(
                rankId=0,
                rankName="",
            )
            rank_id = int(str(char.avatarId) + "0" + str(index + 1))
            rankTemp.rankId = rank_id
            rankTemp.rankName = rankId2Name[str(rank_id)]
            rank_temp.append(rankTemp)
        char_data.rankList = rank_temp

    # 处理命座中的 level_up_skills
    for rank_item in char_data.rankList:
        rank_id = rank_item.rankId
        level_up_skill = AvatarRankSkillUp[str(rank_id)]
        if level_up_skill:
            for item in level_up_skill:
                skill_id = item.id
                skill_up_num = item.num
                # 查找skill_id在不在avatarSkill中
                for index, skill_item in enumerate(char_data.avatarSkill):
                    if str(skill_id) == str(skill_item.skillId):
                        char_data.avatarSkill[index].skillLevel += skill_up_num
                        break

    # 处理基础属性
    base_attributes = AvatarBaseAttributes(
        hp=0,
        attack=0,
        defence=0,
        speed=0,
        CriticalChanceBase=0,
        CriticalDamageBase=0,
        BaseAggro=0,
    )
    avatar_promotion_base = _get_avatar_promotion_config(
        char.avatarId,
        char.promotion,
    )

    # 攻击力
    base_attributes.attack = (
        avatar_promotion_base.AttackBase.Value
        + avatar_promotion_base.AttackAdd.Value * (char.level - 1)
    )
    # 防御力
    base_attributes.defence = (
        avatar_promotion_base.DefenceBase.Value
        + avatar_promotion_base.DefenceAdd.Value * (char.level - 1)
    )
    # 血量
    base_attributes.hp = (
        avatar_promotion_base.HPBase.Value
        + avatar_promotion_base.HPAdd.Value * (char.level - 1)
    )
    # 速度
    base_attributes.speed = avatar_promotion_base.SpeedBase.Value
    # 暴击率
    base_attributes.CriticalChanceBase = avatar_promotion_base.CriticalChance.Value
    # 暴击伤害
    base_attributes.CriticalDamageBase = avatar_promotion_base.CriticalDamage.Value
    # 嘲讽
    base_attributes.BaseAggro = avatar_promotion_base.BaseAggro.Value

    char_data.baseAttributes = base_attributes

    # 处理武器
    equipment_info = AvatarEquipmentInfo(
        equipmentID=0,
        equipmentName="",
        equipmentLevel=0,
        equipmentPromotion=0,
        equipmentRank=0,
        equipmentRarity=0,
        baseAttributes=EquipmentBaseAttributes(hp=0, attack=0, defence=0),
    )
    if char.equipment and char.equipment.tid is not None:
        equipment_info.equipmentID = char.equipment.tid
        equipment_info.equipmentName = EquipmentID2Name[str(char.equipment.tid)]

        equipment_info.equipmentLevel = (
            char.equipment.level if char.equipment.level else 1
        )
        equipment_info.equipmentPromotion = (
            char.equipment.promotion if char.equipment.promotion else 0
        )
        equipment_info.equipmentRank = char.equipment.rank if char.equipment.rank else 0
        equipment_info.equipmentRarity = EquipmentID2Rarity[str(char.equipment.tid)]

        equipment_promotion_base = _get_equipment_promotion_config(
            char.equipment.tid,
            char.equipment.promotion,
        )

        equipment_level = char.equipment.level if char.equipment.level else 1
        # 生命值
        equipment_info.baseAttributes.hp = (
            equipment_promotion_base.BaseHP.Value
            + equipment_promotion_base.BaseHPAdd.Value * (equipment_level - 1)
        )
        # 攻击力
        equipment_info.baseAttributes.attack = (
            equipment_promotion_base.BaseAttack.Value
            + equipment_promotion_base.BaseAttackAdd.Value * (equipment_level - 1)
        )
        # 防御力
        equipment_info.baseAttributes.defence = (
            equipment_promotion_base.BaseDefence.Value
            + equipment_promotion_base.BaseDefenceAdd.Value * (equipment_level - 1)
        )

    char_data.equipmentInfo = equipment_info

    if save_path:
        path = save_path / str(uid)
        path.mkdir(parents=True, exist_ok=True)
        with Path.open(path / f"{char_data.avatarName}.json", "wb") as file:
            _ = file.write(msgjson.encode(char_data))

    return char_data, char_data.avatarName


def _parse_mys_value(value_str: Any) -> float:
    if isinstance(value_str, (int, float)):
        return float(value_str)
    value = str(value_str).strip()
    if value.endswith("%"):
        return float(value[:-1]) / 100
    return float(value)


def _infer_promotion(level: int) -> int:
    if level > 70:
        return 6
    if level > 60:
        return 5
    if level > 50:
        return 4
    if level > 40:
        return 3
    if level > 30:
        return 2
    if level > 20:
        return 1
    return 0


def _get_mys_promotion(source: Any, level: int) -> int:
    promotion_attrs = (
        "promotion",
        "promotion_level",
        "promote_level",
        "promote",
        "promotion_stage",
    )
    for attr_name in promotion_attrs:
        promotion = getattr(source, attr_name, None)
        if promotion is not None:
            return int(promotion)

    max_level_attrs = ("max_level", "max_lv", "maxLevel")
    promotion_by_max_level = {
        20: 0,
        30: 1,
        40: 2,
        50: 3,
        60: 4,
        70: 5,
        80: 6,
    }
    for attr_name in max_level_attrs:
        max_level = getattr(source, attr_name, None)
        try:
            max_level_int = int(max_level)
        except (TypeError, ValueError):
            continue
        if max_level_int in promotion_by_max_level:
            return promotion_by_max_level[max_level_int]

    return _infer_promotion(level)


async def mys_to_dict(
    uid: str,
    nick_name: str,
    mys_avatar_list: list,
    save_path: Union[Path, None] = None,
) -> Tuple[List[str], Dict[str, MihomoCharacter]]:
    """Convert a list of MiYouShe AvatarListItemDetail objects to MihomoCharacter format.

    Args:
        uid: Player UID string.
        nick_name: Player nickname.
        mys_avatar_list: List of AvatarListItemDetail instances from MiYouShe API.
        save_path: Optional directory to save the serialised results.

    Returns:
        Tuple of (char_id_list, char_data_dict) mirroring api_to_dict().
    """
    char_id_list: List[str] = []
    char_data_dict: Dict[str, MihomoCharacter] = {}
    for avatar in mys_avatar_list:
        char_data, avatar_name = await _get_mys_data(avatar, nick_name, uid, save_path)
        avatar_id_str = str(char_data.avatarId)
        if avatar_id_str not in char_id_list:
            char_id_list.append(avatar_id_str)
            char_data_dict[avatar_id_str] = char_data

    if not char_id_list:
        raise CharacterShowcaseNotOpenError(uid)

    return char_id_list, char_data_dict


async def _get_mys_data(
    avatar: Any,
    nick_name: str,
    uid: str,
    save_path: Union[Path, None] = None,
) -> Tuple[MihomoCharacter, str]:
    """Convert a single MiYouShe avatar to MihomoCharacter."""
    avatar_id: int = avatar.id
    level: int = avatar.level
    enhanced_id: int = avatar.cur_enhanced_id if avatar.cur_enhanced_id else 0
    promotion: int = _get_mys_promotion(avatar, level)

    char_data = MihomoCharacter(
        uid=uid,
        nickName=nick_name,
        avatarId=avatar_id,
        avatarName=avatarId2Name[str(avatar_id)],
        avatarElement=avatarId2DamageType[str(avatar_id)],
        avatarRarity=avatarId2Rarity[str(avatar_id)],
        avatarPromotion=promotion,
        avatarLevel=level,
        avatarSkill=[],
        avatarExtraAbility=[],
        avatarAttributeBonus=[],
        RelicInfo=[],
        avatarEnName=avatarId2EnName[str(avatar_id)],
        baseAttributes=AvatarBaseAttributes(
            hp=0,
            attack=0,
            defence=0,
            speed=0,
            CriticalChanceBase=0,
            CriticalDamageBase=0,
            BaseAggro=0,
        ),
        equipmentInfo=AvatarEquipmentInfo(
            equipmentID=0,
            equipmentName="",
            equipmentLevel=0,
            equipmentPromotion=0,
            equipmentRank=0,
            equipmentRarity=0,
            baseAttributes=EquipmentBaseAttributes(hp=0, attack=0, defence=0),
        ),
        rank=0,
        rankList=[],
        enhancedId=enhanced_id,
    )

    # 处理技能
    for skill in getattr(avatar, "skills", None) or []:
        # W-1 fix: skip unactivated skill nodes
        if not skill.is_activated:
            continue

        point_id: int = skill.point_id
        point_id_str = str(point_id)

        # C-2 fix: normalize enhanced point_id for characterSkillTree lookup
        # MYS may prefix enhanced_id (e.g., 11307201 for enhanced avatar 1307)
        # but characterSkillTree uses base avatar_id keys (e.g., 1307201)
        normalized_point_id = point_id
        if enhanced_id and point_id_str.startswith(str(enhanced_id)):
            normalized_point_id = int(point_id_str[len(str(enhanced_id)) :])

        # 主技能: pointId 第5位为 0
        if (
            f"{avatar_id}0" == point_id_str[0:5]
            or f"{enhanced_id}{avatar_id}0" == point_id_str[0:6]
        ):
            skill_id = avatar_id * 100 + point_id % 10 + enhanced_id * 1000000
            if str(skill_id) in skillId2Name:
                skill_temp = MihomoAvatarSkill(
                    skillId=skill_id,
                    skillName=skillId2Name[str(skill_id)],
                    skillEffect=skillId2Effect[str(skill_id)],
                    skillAttackType=skillId2AttackType[str(skill_id)],
                    skillLevel=skill.level,
                )
                char_data.avatarSkill.append(skill_temp)

        # 额外能力: pointId 第5位为 1
        elif (
            f"{avatar_id}1" == point_id_str[0:5]
            or f"{enhanced_id}{avatar_id}1" == point_id_str[0:6]
        ):
            extra_ability_temp = MihomoAvatarExtraAbility(
                extraAbilityId=point_id,
                extraAbilityLevel=skill.level,
            )
            char_data.avatarExtraAbility.append(extra_ability_temp)

        # 属性加成: pointId 第5位为 2
        elif (
            f"{avatar_id}2" == point_id_str[0:5]
            or f"{enhanced_id}{avatar_id}2" == point_id_str[0:6]
        ):
            attribute_bonus_temp = MihomoAvatarAttributeBonus(
                attributeBonusId=point_id,
                attributeBonusLevel=skill.level,
                statusAdd=AttributeBounsStatusAdd(
                    property_="",
                    name="",
                    value=0,
                ),
            )
            # C-2 fix: use base avatar_id for characterSkillTree lookup
            tree_key = str(avatar_id)
            pid_key = str(normalized_point_id)
            if (
                tree_key in characterSkillTree
                and pid_key in characterSkillTree[tree_key]
            ):
                status_add = (
                    characterSkillTree[tree_key][pid_key]
                    .levels[skill.level - 1]
                    .properties
                )
                for property_ in status_add:
                    attribute_bonus_temp.statusAdd.property_ = property_.type
                    attribute_bonus_temp.statusAdd.name = Property2Name[property_.type]
                    attribute_bonus_temp.statusAdd.value = property_.value
                    char_data.avatarAttributeBonus.append(attribute_bonus_temp)

    # 处理遗器 (relics + ornaments)
    all_relics = list(getattr(avatar, "relics", None) or []) + list(
        getattr(avatar, "ornaments", None) or []
    )
    for relic in all_relics:
        relic_id: int = relic.id
        main_prop_type = str(relic.main_property.property_type)
        main_property_name = MysPropertyType2Property[main_prop_type]
        main_property_value = _parse_mys_value(relic.main_property.value)

        relic_temp = Relic(
            relicId=relic_id,
            relicName=ItemId2Name[str(relic_id)],
            SetId=RelicId2SetId[str(relic_id)],
            SetName=SetId2Name[str(RelicId2SetId[str(relic_id)])],
            Type=relic.pos,
            MainAffix=RelicMainAffix(
                AffixID=relic.main_property.property_type,
                Property=main_property_name,
                Name=Property2Name[main_property_name],
                Value=main_property_value,
            ),
            SubAffixList=[],
            Level=relic.level,
        )

        for sub in relic.properties:
            sub_property_name = MysPropertyType2Property[str(sub.property_type)]
            sub_affix_temp = RelicSubAffix(
                SubAffixID=sub.property_type,
                Property=sub_property_name,
                Name=Property2Name[sub_property_name],
                Cnt=sub.times,
                Step=0,
                Value=_parse_mys_value(sub.value),
            )
            relic_temp.SubAffixList.append(sub_affix_temp)

        char_data.RelicInfo.append(relic_temp)

    # 处理命座
    rank_temp: List[RankData] = []
    unlocked_ranks = [
        rank
        for rank in (getattr(avatar, "ranks", None) or [])
        if getattr(rank, "is_unlocked", False)
    ]
    char_data.rank = len(unlocked_ranks)
    for r in unlocked_ranks:
        rankTemp = RankData(
            rankId=r.id,
            rankName=rankId2Name.get(str(r.id), ""),
        )
        rank_temp.append(rankTemp)
    char_data.rankList = rank_temp

    # 处理命座中的 level_up_skills
    for rank_item in char_data.rankList:
        rank_id = rank_item.rankId
        level_up_skill = AvatarRankSkillUp.get(str(rank_id))
        if level_up_skill:
            for item in level_up_skill:
                skill_id = item.id
                skill_up_num = item.num
                for index, skill_item in enumerate(char_data.avatarSkill):
                    if str(skill_id) == str(skill_item.skillId):
                        char_data.avatarSkill[index].skillLevel += skill_up_num
                        break

    # 处理基础属性 (from AvatarPromotionConfig, NOT MYS properties)
    # MYS properties.base includes equipment base stats which would cause double-counting
    avatar_promotion_base = _get_avatar_promotion_config(avatar_id, promotion)

    char_data.baseAttributes = AvatarBaseAttributes(
        hp=(
            avatar_promotion_base.HPBase.Value
            + avatar_promotion_base.HPAdd.Value * (level - 1)
        ),
        attack=(
            avatar_promotion_base.AttackBase.Value
            + avatar_promotion_base.AttackAdd.Value * (level - 1)
        ),
        defence=(
            avatar_promotion_base.DefenceBase.Value
            + avatar_promotion_base.DefenceAdd.Value * (level - 1)
        ),
        speed=avatar_promotion_base.SpeedBase.Value,
        CriticalChanceBase=avatar_promotion_base.CriticalChance.Value,
        CriticalDamageBase=avatar_promotion_base.CriticalDamage.Value,
        BaseAggro=avatar_promotion_base.BaseAggro.Value,
    )

    # 处理武器
    equipment_info = AvatarEquipmentInfo(
        equipmentID=0,
        equipmentName="",
        equipmentLevel=0,
        equipmentPromotion=0,
        equipmentRank=0,
        equipmentRarity=0,
        baseAttributes=EquipmentBaseAttributes(hp=0, attack=0, defence=0),
    )
    if avatar.equip is not None:
        equip = avatar.equip
        equip_id: int = equip.id
        equip_level: int = equip.level if equip.level else 1
        equip_promotion = _get_mys_promotion(equip, equip_level)

        equipment_info.equipmentID = equip_id
        equipment_info.equipmentName = EquipmentID2Name[str(equip_id)]
        equipment_info.equipmentLevel = equip_level
        equipment_info.equipmentPromotion = equip_promotion
        equipment_info.equipmentRank = equip.rank if equip.rank else 0
        equipment_info.equipmentRarity = EquipmentID2Rarity.get(
            str(equip_id), equip.rarity
        )

        equipment_promotion_base = _get_equipment_promotion_config(
            equip_id,
            equip_promotion,
        )

        equipment_info.baseAttributes.hp = (
            equipment_promotion_base.BaseHP.Value
            + equipment_promotion_base.BaseHPAdd.Value * (equip_level - 1)
        )
        equipment_info.baseAttributes.attack = (
            equipment_promotion_base.BaseAttack.Value
            + equipment_promotion_base.BaseAttackAdd.Value * (equip_level - 1)
        )
        equipment_info.baseAttributes.defence = (
            equipment_promotion_base.BaseDefence.Value
            + equipment_promotion_base.BaseDefenceAdd.Value * (equip_level - 1)
        )

    char_data.equipmentInfo = equipment_info

    if save_path:
        path = save_path / str(uid)
        path.mkdir(parents=True, exist_ok=True)
        with Path.open(path / f"{char_data.avatarName}.json", "wb") as file:
            _ = file.write(msgjson.encode(char_data))

    return char_data, char_data.avatarName
