from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class BreastUVs(BaseModel):
    skin: LayerUVs = Field(default_factory=lambda: LayerUVs.default_skin())
    overlay: LayerUVs = Field(default_factory=lambda: LayerUVs.default_overlay())


class LayerUVs(BaseModel):
    left: dict[UVSide, Annotated[list[int], Field(min_length=4, max_length=4)]]
    right: dict[UVSide, Annotated[list[int], Field(min_length=4, max_length=4)]]

    @classmethod
    def default_skin(cls) -> LayerUVs:
        return LayerUVs(
            left={
                UVSide.east: [24, 21, 27, 26],
                UVSide.west: [16, 21, 20, 26],
                UVSide.down: [20, 17, 24, 21],
                UVSide.up: [20, 25, 24, 27],
                UVSide.north: [20, 21, 24, 26],
            },
            right={
                UVSide.east: [28, 21, 32, 26],
                UVSide.west: [21, 21, 24, 26],
                UVSide.down: [24, 17, 28, 21],
                UVSide.up: [24, 25, 28, 27],
                UVSide.north: [24, 21, 28, 26],
            },
        )

    @classmethod
    def default_overlay(cls) -> LayerUVs:
        return LayerUVs(
            left={
                UVSide.west: [17, 37, 20, 42],
                UVSide.down: [20, 34, 24, 37],
                UVSide.up: [20, 41, 24, 44],
                UVSide.north: [20, 37, 24, 42],
            },
            right={
                UVSide.east: [28, 37, 31, 42],
                UVSide.down: [24, 34, 28, 37],
                UVSide.up: [24, 41, 28, 44],
                UVSide.north: [24, 37, 28, 42],
            },
        )

    @field_validator("left", "right")
    @classmethod
    def validate_quad(cls, value: dict[UVSide, list[int]]) -> dict[UVSide, list[int]]:
        for (side, quad) in value.items():
            # should be caught by min_length and max_length, but still double check just to be safe while we're here
            if len(quad) != 4:
                raise ValueError(f"Invalid side {side.value}: expected exactly 4 coordinate positions")
            elif not all(0 <= x <= 64 for x in quad):
                raise ValueError(f"Invalid side {side.value}: contained UV coordinates must be within 0..64")
        return value


class UVSide(StrEnum):
    down = "down"
    up = "up"
    east = "east"
    west = "west"
    north = "north"
