from __future__ import annotations

from pydantic import BaseModel, UUID4

from db import UserConfig, Gender


class BulkQueryResponse(BaseModel):
    success: bool = True
    users: dict[UUID4, UserData]


class UserData(BaseModel):
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

    @classmethod
    def from_db(cls, user: UserConfig | None) -> UserData | None:
        if user is None:
            return None

        return UserData(
            gender=user.gender,
            bust_size=user.bust_size,
            hurt_sounds=user.hurt_sounds,
            breasts_xOffset=user.breasts_xOffset,
            breasts_yOffset=user.breasts_yOffset,
            breasts_zOffset=user.breasts_zOffset,
            breasts_uniboob=user.breasts_uniboob,
            breasts_cleavage=user.breasts_cleavage,
            breast_physics=user.breast_physics,
            show_in_armor=user.show_in_armor,
            bounce_multiplier=user.bounce_multiplier,
            floppy_multiplier=user.floppy_multiplier,
            voice_pitch=user.voice_pitch,
            holiday_themes=user.holiday_themes,
        )

    def to_db(self) -> UserConfig:
        return UserConfig(
            gender=Gender.from_ordinal(self.gender),
            bust_size=self.bust_size,
            hurt_sounds=self.hurt_sounds,
            breasts_xOffset=self.breasts_xOffset,
            breasts_yOffset=self.breasts_yOffset,
            breasts_zOffset=self.breasts_zOffset,
            breasts_uniboob=self.breasts_uniboob,
            breasts_cleavage=self.breasts_cleavage,
            breast_physics=self.breast_physics,
            show_in_armor=self.show_in_armor,
            bounce_multiplier=self.bounce_multiplier,
            floppy_multiplier=self.floppy_multiplier,
            voice_pitch=self.voice_pitch,
            holiday_themes=self.holiday_themes,
        )
