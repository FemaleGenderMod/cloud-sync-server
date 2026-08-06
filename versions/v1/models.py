from __future__ import annotations

from typing import Any

from pydantic import BaseModel, UUID4

from db import UserConfig


class BulkQueryResponse(BaseModel):
    success: bool = True
    users: dict[UUID4, UserData]


class UserData(BaseModel):
    @classmethod
    def from_db(cls, user: UserConfig):
        cls(**user.model_dump(round_trip=True))

    def to_db(self) -> UserConfig:
        return UserConfig(**self.model_dump(round_trip=True))

    gender: int = 1

    bust_size: float = 0.6
    hurt_sounds: bool = True

    breasts_xOffset: float = 0.0
    breasts_yOffset: float = 0.0
    breasts_zOffset: float = 0.0
    breasts_uniboob: bool = True
    breasts_cleavage: float = 0.0

    breast_physics: bool = True
    show_in_armor: bool = True
    bounce_multiplier: float = 0.333
    floppy_multiplier: float = 0.75

    voice_pitch: float = 1.0
    holiday_themes: bool = True
