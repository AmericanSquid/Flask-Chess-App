from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    pass


class GameStatus(StrEnum):
    ACTIVE = "active"
    FINISHED = "finished"


class ResultCode(StrEnum):
    ONGOING = "*"
    WHITE_WIN = "1-0"
    BLACK_WIN = "0-1"
    DRAW = "1/2-1/2"
