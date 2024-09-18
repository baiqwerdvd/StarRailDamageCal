import json
from pathlib import Path
from typing import List

from ...damage.Base.model import (
    DamageInstanceAvatar,
)
from ...model import MihomoAvatarSkill

path = Path(__file__).parent.parent
with Path.open(path / "Excel" / "SkillData.json", encoding="utf-8") as f:
    skill_dict = json.load(f)


skill_types = {
    "Normal": "Normal_",
    "BPSkill": "BPSkill_",
    "Ultra": "Ultra_",
    "Maze": "Maze_",
    "": "Talent_",
}


class SingleSkill:
    def __init__(self, skill: MihomoAvatarSkill):
        self.id = skill.skillId
        self.level = skill.skillLevel


class BaseSkills:
    Normal_: SingleSkill
    BPSkill_: SingleSkill
    Ultra_: SingleSkill
    Maze_: SingleSkill
    Talent_: SingleSkill

    @classmethod
    def create(cls, char: DamageInstanceAvatar, skills: List[MihomoAvatarSkill]):
        for skill in skills:
            skill_attack_type = skill.skillAttackType
            if skill_attack_type not in skill_types:
                msg = f"Unknown skillAttackType: {skill_attack_type}"
                raise ValueError(msg)
            setattr(cls, skill_types[skill_attack_type], SingleSkill(skill))
        return cls
