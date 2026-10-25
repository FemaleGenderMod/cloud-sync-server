from __future__ import annotations

import enum
import os
from datetime import datetime
from typing import Annotated, Literal, ClassVar, cast

from beanie import Document, init_beanie, Indexed
from pydantic import BaseModel, UUID4
from pymongo import AsyncMongoClient

from core.util import Lazy
from core.uvs import BreastUVs

NamedGender = Literal["male", "female", "other"]


class Gender(enum.IntEnum):
    FROM_NAME: ClassVar[dict[NamedGender, Gender]] = Lazy(
        lambda: {"male": Gender.MALE, "female": Gender.FEMALE, "other": Gender.OTHER}
    )
    TO_NAME: ClassVar[dict[Gender, NamedGender]] = Lazy(
        lambda: {v: k for k, v in Gender.FROM_NAME.items()}
    )
    FROM_ID: ClassVar[dict[Gender, NamedGender]] = Lazy(
        lambda: {i: Gender(i) for i in range(len(Gender))}
    )

    FEMALE = 0
    MALE = 1
    OTHER = 2

    @property
    def named(self) -> NamedGender:
        return cast(NamedGender, Gender.TO_NAME[self])

    @staticmethod
    def from_ordinal(ordinal: int) -> Gender:
        return Gender.FROM_ID[ordinal % len(Gender)]

    @classmethod
    def from_name(cls, gender: NamedGender) -> Gender:
        value = Gender.FROM_NAME[gender]
        if value is None:
            raise ValueError(f"unknown gender value {gender!r}")
        return value


class UserAuth(Document):
    uuid: UUID4
    token: Annotated[str, Indexed(unique=True)]
    created_at: Annotated[datetime, Indexed(expireAfterSeconds=60 * 60)]


# note: any new fields added here must also be reflected in the relevant api version models as well
# TODO add a migration to convert this to be similar to the new config file structure
class UserConfig(BaseModel):
    gender: Gender = Gender.MALE

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
    uvs: BreastUVs | None = None


class User(Document):
    uuid: Annotated[UUID4, Indexed()]
    data: UserConfig | None

    @classmethod
    async def find_one_or_create(cls, uuid: UUID4) -> User:
        existing = await cls.find_one(User.uuid == uuid)
        return existing or cls(uuid=uuid, data=UserConfig())


async def init_db():
    host = os.environ.get("MONGO_HOST", "mongodb://localhost:27017")
    client = AsyncMongoClient(host, connectTimeoutMS=5_000)
    await init_beanie(database=client["wfgm-sync"], document_models=[User, UserAuth])
