# ruff: noqa: S101

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from msgspec import convert

from starrail_damage_cal.damage.AvatarDamage.AvatarDamage import AvatarDamage
from starrail_damage_cal.damage.Base.AvatarBase import build_base_avatar_attribute
from starrail_damage_cal.damage.Base.model import DamageInstance, DamageInstanceAvatar
from starrail_damage_cal.damage.Base.SkillBase import BaseSkills
from starrail_damage_cal.damage.Role import apply_attribute_bonus
from starrail_damage_cal.exception import UnsupportedAvatarError
from starrail_damage_cal.mihomo.models import Avatar
from starrail_damage_cal.model import (
    AvatarBaseAttributes,
    AvatarEquipmentInfo,
    EquipmentBaseAttributes,
    MihomoCharacter,
)
from starrail_damage_cal.mono.Character import Character
from starrail_damage_cal.to_data import (
    _get_avatar_promotion_config,
    _get_equipment_promotion_config,
    _get_mys_data,
    get_data,
)


def load_avatar_detail() -> dict:
    raw_data = json.loads(Path("test/test.json").read_text(encoding="utf-8"))
    return raw_data["detailInfo"]["avatarDetailList"][0]


def test_build_base_avatar_attribute_uses_requested_promotion():
    promotion_zero = build_base_avatar_attribute(1001, 0, 80)
    promotion_six = build_base_avatar_attribute(1001, 6, 80)

    assert promotion_zero.attack == 344.52
    assert promotion_six.attack == 511.56
    assert promotion_six.hp == 1058.4
    assert promotion_six.attack > promotion_zero.attack


def test_avatar_promotion_lookup_normalizes_zero_promotion():
    promotion = _get_avatar_promotion_config(1302, 0)

    assert promotion.AvatarID == 1302
    assert promotion.MaxLevel == 20


def test_equipment_promotion_lookup_normalizes_zero_promotion():
    promotion = _get_equipment_promotion_config(20000, 0)

    assert promotion.EquipmentID == 20000
    assert promotion.MaxLevel == 20


def test_base_skills_create_returns_independent_objects():
    class SkillStub:
        def __init__(self, skill_attack_type: str, skill_level: int):
            self.skillAttackType = skill_attack_type
            self.skillLevel = skill_level
            self.skillId = 0

    first = BaseSkills.create(
        char=None,
        skills=[
            SkillStub("Normal", 1),
            SkillStub("BPSkill", 2),
            SkillStub("Ultra", 3),
            SkillStub("", 4),
        ],
    )
    second = BaseSkills.create(
        char=None,
        skills=[
            SkillStub("Normal", 7),
            SkillStub("BPSkill", 8),
            SkillStub("Ultra", 9),
            SkillStub("", 10),
        ],
    )

    assert first is not second
    assert first.Normal_.level == 1
    assert first.BPSkill_.level == 2
    assert second.Normal_.level == 7
    assert second.BPSkill_.level == 8


def test_apply_attribute_bonus_initializes_missing_common_keys():
    result = apply_attribute_bonus(
        {"BPSkill1AttackAddedRatio": 0.3},
        "BPSkill1",
        "BPSkill1",
    )

    assert result["AttackAddedRatio"] == 0.3


def test_avatar_damage_create_raises_for_unsupported_avatar():
    avatar = DamageInstanceAvatar(
        id_=9999,
        level=80,
        rank=0,
        element="Fire",
        promotion=6,
        attribute_bonus=[],
        extra_ability=[],
    )

    with pytest.raises(UnsupportedAvatarError, match="Unsupported avatar id: 9999"):
        AvatarDamage.create(avatar, [])


def test_damage_instance_leaves_weapon_none_without_equipment():
    char = MihomoCharacter(
        uid="1",
        nickName="tester",
        avatarId=1001,
        avatarName="三月七",
        avatarElement="Ice",
        avatarRarity="4",
        avatarLevel=80,
        avatarPromotion=6,
        avatarSkill=[],
        avatarExtraAbility=[],
        avatarAttributeBonus=[],
        RelicInfo=[],
        avatarEnName="March 7th",
        baseAttributes=AvatarBaseAttributes(
            hp=1,
            attack=1,
            defence=1,
            speed=1,
            CriticalChanceBase=0.05,
            CriticalDamageBase=0.5,
            BaseAggro=150,
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
        enhancedId=0,
    )

    assert DamageInstance(Character(char)).weapon is None


@pytest.mark.asyncio
async def test_get_data_applies_rank_skill_bonus_without_relics():
    avatar_raw = load_avatar_detail()
    avatar_raw["rank"] = 3
    avatar_raw["relicList"] = []

    avatar = convert(avatar_raw, type=Avatar)
    char_data, _ = await get_data(avatar, "tester", "100000001")
    skill_levels = {skill.skillId: skill.skillLevel for skill in char_data.avatarSkill}

    assert skill_levels[121203] == 12
    assert skill_levels[121204] == 12


@pytest.mark.asyncio
async def test_get_data_uses_zero_promotion_config():
    avatar = SimpleNamespace(
        avatarId=1001,
        promotion=0,
        level=20,
        skillTreeList=[],
        relicList=[],
        rank=0,
        equipment=None,
        enhancedId=0,
    )

    char_data, _ = await get_data(avatar, "tester", "100000001")
    expected = build_base_avatar_attribute(1001, 0, 20)

    assert char_data.avatarPromotion == 0
    assert char_data.baseAttributes.attack == expected.attack
    assert char_data.baseAttributes.hp == expected.hp


@pytest.mark.asyncio
async def test_get_mys_data_uses_zero_promotion_config():
    avatar = SimpleNamespace(
        id=1302,
        level=20,
        promotion=0,
        cur_enhanced_id=0,
        skills=[],
        relics=[],
        ornaments=[],
        ranks=[],
        equip=None,
    )

    char_data, avatar_name = await _get_mys_data(avatar, "tester", "100000001")
    expected = build_base_avatar_attribute(1302, 0, 20)

    assert avatar_name == "银枝"
    assert char_data.avatarPromotion == 0
    assert char_data.baseAttributes.attack == expected.attack
    assert char_data.baseAttributes.hp == expected.hp
