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
        del char
        skill_data = cls()
        for skill_name in skill_types.values():
            setattr(skill_data, skill_name, None)
        for skill in skills:
            skill_attack_type = skill.skillAttackType
            if skill_attack_type not in skill_types:
                msg = f"Unknown skillAttackType: {skill_attack_type}"
                raise ValueError(msg)
            setattr(skill_data, skill_types[skill_attack_type], SingleSkill(skill))

        required_skills = ("Normal_", "BPSkill_", "Ultra_", "Talent_")
        missing_skills = [
            skill_name
            for skill_name in required_skills
            if getattr(skill_data, skill_name) is None
        ]
        if missing_skills:
            msg = f"Missing required skills: {', '.join(missing_skills)}"
            raise ValueError(msg)

        return skill_data
