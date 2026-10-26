from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from core.util import expect_value


class BreastUVs(BaseModel):
    skin: LayerUVs = Field(default_factory=lambda: LayerUVs.default_skin())
    overlay: LayerUVs = Field(default_factory=lambda: LayerUVs.default_overlay())


class LayerUVs(BaseModel):
    left: UVMapping
    right: UVMapping

    @classmethod
    def default_skin(cls) -> LayerUVs:
        return LayerUVs(
            left=UVMapping(
                east=[24, 21, 27, 26],
                west=[16, 21, 20, 26],
                down=[20, 17, 24, 21],
                up=[20, 25, 24, 27],
                north=[20, 21, 24, 26],
            ),
            right=UVMapping(
                east=[28, 21, 32, 26],
                west=[21, 21, 24, 26],
                down=[24, 17, 28, 21],
                up=[24, 25, 28, 27],
                north=[24, 21, 28, 26],
            ),
        )

    @classmethod
    def default_overlay(cls) -> LayerUVs:
        return LayerUVs(
            left=UVMapping(
                east=UVMapping.unused(),
                west=[17, 37, 20, 42],
                down=[20, 34, 24, 37],
                up=[20, 34, 24, 37],
                north=[20, 37, 24, 42],
            ),
            right=UVMapping(
                east=[28, 37, 31, 42],
                west=UVMapping.unused(),
                down=[24, 34, 28, 37],
                up=[24, 41, 28, 44],
                north=[24, 37, 28, 42],
            ),
        )


class UVMapping(BaseModel):
    down: list[int] = Field(min_length=4, max_length=4)
    up: list[int] = Field(min_length=4, max_length=4)
    east: list[int] = Field(min_length=4, max_length=4)
    west: list[int] = Field(min_length=4, max_length=4)
    north: list[int] = Field(min_length=4, max_length=4)

    @classmethod
    def unused(cls) -> list[int]:
        return [0, 0, 0, 0]

    @field_validator("down", "up", "east", "west", "north")
    @classmethod
    def validate_side(cls, value: list[int]) -> list[int]:
        # technically redundant with min_length=4 and max_length=4, but doesn't hurt to check
        # that this is correct while we're here anyway
        expect_value(len(value) == 4, lambda: f"Expected exactly 4 coordinate positions")
        expect_value(all(0 <= x <= 64 for x in value), lambda: f"Contained UV coordinates must be within 0..64")

        return value
