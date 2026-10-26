from __future__ import annotations

from pydantic import BaseModel, UUID4, Field

from core.db import UserConfig, Gender
from core.uvs import LayerUVs, UVMapping, BreastUVs


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

    leftBreastUVLayout: OldUVMapping = Field(
        default_factory=lambda: OldUVMapping.from_modern(LayerUVs.default_skin().left)
    )
    rightBreastUVLayout: OldUVMapping = Field(
        default_factory=lambda: OldUVMapping.from_modern(LayerUVs.default_skin().right)
    )
    leftBreastOverlayUVLayout: OldUVMapping = Field(
        default_factory=lambda: OldUVMapping.from_modern(LayerUVs.default_overlay().left)
    )
    rightBreastOverlayUVLayout: OldUVMapping = Field(
        default_factory=lambda: OldUVMapping.from_modern(LayerUVs.default_overlay().right)
    )

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
            leftBreastUVLayout=OldUVMapping.from_modern(user.uvs.skin.left),
            rightBreastUVLayout=OldUVMapping.from_modern(user.uvs.skin.right),
            leftBreastOverlayUVLayout=OldUVMapping.from_modern(user.uvs.overlay.left),
            rightBreastOverlayUVLayout=OldUVMapping.from_modern(user.uvs.overlay.right),
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
            uvs=BreastUVs(
                skin=LayerUVs(
                    left=self.leftBreastUVLayout.to_modern(),
                    right=self.rightBreastUVLayout.to_modern(),
                ),
                overlay=LayerUVs(
                    left=self.leftBreastOverlayUVLayout.to_modern(),
                    right=self.rightBreastOverlayUVLayout.to_modern(),
                ),
            ),
        )


# I do not like having to support these older versions
class OldUVMapping(BaseModel):
    down: OldUVMappingEntry
    up: OldUVMappingEntry
    east: OldUVMappingEntry
    west: OldUVMappingEntry
    north: OldUVMappingEntry

    @classmethod
    def from_modern(cls, mapping: UVMapping) -> OldUVMapping:
        return OldUVMapping(
            down=OldUVMappingEntry(
                x1=mapping.down[0],
                y1=mapping.down[1],
                x2=mapping.down[2],
                y2=mapping.down[3],
            ),
            up=OldUVMappingEntry(
                x1=mapping.up[0],
                y1=mapping.up[1],
                x2=mapping.up[2],
                y2=mapping.up[3],
            ),
            east=OldUVMappingEntry(
                x1=mapping.east[0],
                y1=mapping.east[1],
                x2=mapping.east[2],
                y2=mapping.east[3],
            ),
            west=OldUVMappingEntry(
                x1=mapping.west[0],
                y1=mapping.west[1],
                x2=mapping.west[2],
                y2=mapping.west[3],
            ),
            north=OldUVMappingEntry(
                x1=mapping.north[0],
                y1=mapping.north[1],
                x2=mapping.north[2],
                y2=mapping.north[3],
            ),
        )

    def to_modern(self) -> UVMapping:
        return UVMapping(
            down=[
                self.down.x1,
                self.down.y1,
                self.down.x2,
                self.down.y2,
            ],
            up=[
                self.up.x1,
                self.up.y1,
                self.up.x2,
                self.up.y2,
            ],
            east=[
                self.east.x1,
                self.east.y1,
                self.east.x2,
                self.east.y2,
            ],
            west=[
                self.west.x1,
                self.west.y1,
                self.west.x2,
                self.west.y2,
            ],
            north=[
                self.north.x1,
                self.north.y1,
                self.north.x2,
                self.north.y2,
            ],
        )


class OldUVMappingEntry(BaseModel):
    x1: int = Field(ge=0, le=64, examples=[0])
    y1: int = Field(ge=0, le=64, examples=[0])
    x2: int = Field(ge=0, le=64, examples=[0])
    y2: int = Field(ge=0, le=64, examples=[0])
