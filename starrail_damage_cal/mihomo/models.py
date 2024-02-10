from typing import List, Union

from msgspec import Struct, field


class Behavior(Struct):
    pointId: int
    level: int


class Equipment(Struct):
    level: Union[int, None] = field(default=0)
    tid: Union[int, None] = None
    promotion: Union[int, None] = field(default=0)
    rank: Union[int, None] = field(default=0)


class SubAffix(Struct):
    affixId: int
    cnt: int
    step: Union[int, None] = field(default=0)


class Relic(Struct):
    tid: int
    mainAffixId: int
    type_: int = field(name="type")
    subAffixList: Union[List[SubAffix], None] = field(default=[])
    level: Union[int, None] = field(default=0)


class Avatar(Struct):
    skillTreeList: List[Behavior]
    avatarId: int
    level: int
    equipment: Union[Equipment, None] = None
    relicList: Union[List[Relic], None] = field(default=[])
    pos: Union[int, None] = field(default=0)
    rank: Union[int, None] = field(default=0)
    promotion: Union[int, None] = field(default=0)


class Challenge(Struct):
    scheduleMaxLevel: Union[int, None] = None
    MazeGroupIndex: Union[int, None] = None
    PreMazeGroupIndex: Union[int, None] = None


class ChallengeInfo(Struct):
    scheduleMaxLevel: Union[int, None] = None
    scheduleGroupId: Union[int, None] = None
    noneScheduleMaxLevel: Union[int, None] = None


class PlayerSpaceInfo(Struct):
    avatarCount: int
    challengeInfo: ChallengeInfo
    achievementCount: Union[int, None] = field(default=0)
    equipmentCount: Union[int, None] = field(default=0)
    maxRogueChallengeScore: Union[int, None] = field(default=0)


class PlayerDetailInfo(Struct):
    assistAvatarList: Union[List[Avatar], None]
    platform: Union[int, str]
    isDisplayAvatar: bool
    uid: int
    nickname: str
    level: int
    recordInfo: Union[PlayerSpaceInfo, None]
    headIcon: int
    friendCount: Union[int, None] = field(default=0)
    worldLevel: Union[int, None] = field(default=0)
    avatarDetailList: Union[List[Avatar], None] = None
    signature: Union[str, None] = None
    Birthday: Union[int, None] = None


class MihomoData(Struct):
    detailInfo: PlayerDetailInfo
