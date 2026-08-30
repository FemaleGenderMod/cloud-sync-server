from __future__ import annotations

import enum
import os
from datetime import datetime
from typing import Annotated, Literal, ClassVar, cast

from beanie import Document, init_beanie, Indexed
from pydantic import BaseModel, UUID4
from pymongo import AsyncMongoClient

from core.util import Lazy

NamedGender = Literal["male", "female", "other"]


class Gender(enum.IntEnum):
    FROM_NAME: ClassVar[dict[NamedGender, Gender]] = Lazy(lambda: {"male": Gender.MALE, "female": Gender.FEMALE, "other": Gender.OTHER})
    TO_NAME: ClassVar[dict[Gender, NamedGender]] = Lazy(lambda: {v: k for k, v in Gender.FROM_NAME.items()})
    FROM_ID: ClassVar[dict[Gender, NamedGender]] = Lazy(lambda: {i: Gender(i) for i in range(len(Gender))})

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


# TODO these property docstrings are not shown in the generated OpenAPI model docs :(
class ContributorNametag(BaseModel):
    text: str
    """Text displayed instead of the normal contributor nametag.

    This value is ignored on versions that support ``roles``, but is still required
    for backwards compatibility with versions that do not support it."""

    name: str | None = None
    """Optional; the contributor's display name. This does not have to match the username of the
    associated Minecraft account.

    This must be set for a contributor to be displayed in the in-game credits screen.

    If this is not set and there exists a contributor with the same UUID in the mod's built-in
    list of contributors, this contributor entry will be entirely ignored."""

    color: int | None = None
    """"Optional; packed RGB color used for the nametag above a contributor's head, and in various other UIs.

    This may be null to use the regular contributor color."""

    roles: int = 0
    """Bitmask referring to how this user has contributed to the mod, with the following
    possible enum values (in order of how they're listed):

    - MOD_CREATOR
    - FABRIC_MAINTAINER
    - NEOFORGE_MAINTAINER
    - DEVELOPER
    - TRANSLATOR
    - MASCOT
    - VOICE_ACTOR_FEMALE
    - GENERIC

    Note that the mod currently (as of 4.3.5 on 1.21.9) only uses the topmost role defined in the bitmask,
    and all additional roles defined (if any) are ignored."""

    show_in_credits: bool = True
    """If this is false, this contributor will not be shown in the credits screen, even if
    a valid ``name`` is specified."""


class User(Document):
    uuid: Annotated[UUID4, Indexed()]
    data: UserConfig | None
    nametag: ContributorNametag | None = None

    @classmethod
    async def find_one_or_create(cls, uuid: UUID4) -> User:
        existing = await cls.find_one(User.uuid == uuid)
        return existing or cls(uuid=uuid, data=UserConfig())


async def init_db():
    host = os.environ.get("MONGO_HOST", "mongodb://localhost:27017")
    client = AsyncMongoClient(host, connectTimeoutMS=5_000)
    await init_beanie(database=client["wfgm-sync"], document_models=[User, UserAuth])
