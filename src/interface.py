from enum import Enum
from typing import List

from pydantic import BaseModel


class CommandGroups(Enum):
    ...


class ShowAvatarInfo(BaseModel):
    avatarId: int
    level: int


class AvatarInfo(BaseModel):
    avatarId: int


class PlayerInfo(BaseModel):
    nickname: str
    level: int
    worldLevel: int
    nameCardId: int
    finishAchievementNum: int
    towerFloorIndex: int
    towerLevelIndex: int
    showAvatarInfoList: List[ShowAvatarInfo]
    showNameCardIdList: List[int]
    profilePicture: int
