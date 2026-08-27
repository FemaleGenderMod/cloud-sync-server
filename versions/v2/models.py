from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, UUID4

from core.db import UserConfig, Gender


class BulkQueryResponse(BaseModel):
    success: bool = True
    users: dict[UUID4, UserData]


class AuthenticationBody(BaseModel):
    server_id: str
    username: str


class UserData(BaseModel):
    gender: Literal["male", "female", "other"] = "male"
    breasts: BreastsData = Field(default_factory=lambda: BreastsData())
    sound: SoundData = Field(default_factory=lambda: SoundData())
    show_in_armor: bool = True

    @classmethod
    def from_db(cls, user: UserConfig | None) -> UserData | None:
        if user is None:
            return None

        return UserData(
            gender=user.gender.named,
            breasts=BreastsData(
                size=user.bust_size,
                cleavage=user.breasts_cleavage,
                offset=[user.breasts_xOffset, user.breasts_yOffset, user.breasts_zOffset],
                physics=BreastPhysicsData(
                    enabled=user.breast_physics,
                    bounce_multiplier=user.bounce_multiplier,
                    floppiness=user.floppy_multiplier,
                    uniboob=user.breasts_uniboob,
                ),
            ),
            sound=SoundData(
                override_hurt=user.hurt_sounds,
                voice_pitch=user.voice_pitch,
            ),
            show_in_armor=user.show_in_armor,
        )

    def to_db(self) -> UserConfig:
        return UserConfig(
            gender=Gender.from_name(self.gender),
            bust_size=self.breasts.size,
            hurt_sounds=self.sound.override_hurt,
            breasts_xOffset=self.breasts.offset[0],
            breasts_yOffset=self.breasts.offset[1],
            breasts_zOffset=self.breasts.offset[2],
            breasts_uniboob=self.breasts.physics.uniboob,
            breasts_cleavage=self.breasts.cleavage,
            breast_physics=self.breasts.physics.enabled,
            show_in_armor=self.show_in_armor,
            bounce_multiplier=self.breasts.physics.bounce_multiplier,
            floppy_multiplier=self.breasts.physics.floppiness,
            voice_pitch=self.sound.voice_pitch,
        )


class BreastsData(BaseModel):
    size: float = 0.6
    cleavage: float = 0.0
    offset: list[float] = Field(min_length=3, max_length=3, default_factory=lambda: [0, 0, 0])
    physics: BreastPhysicsData = Field(default_factory=lambda: BreastPhysicsData())


class BreastPhysicsData(BaseModel):
    enabled: bool = True
    bounce_multiplier: float = 0.333
    floppiness: float = 0.75
    uniboob: bool = True


class SoundData(BaseModel):
    override_hurt: bool = True
    voice_pitch: float = 1.0
