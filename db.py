from __future__ import annotations

import enum
import os
from datetime import timedelta, datetime
from typing import Annotated

from beanie import Document, init_beanie, Indexed
from pydantic import BaseModel, UUID4
from pymongo import AsyncMongoClient


# fastapi docs suck for enums, so just document the ordinals in the doc string here
class Gender(enum.IntEnum):
    """Integer value referencing the ordinal value of the Gender enum in the mod

    - `FEMALE`: 0
    - `MALE`: 1
    - `OTHER`: 2
    """

    FEMALE = 0
    MALE = 1
    OTHER = 2


class UserAuth(Document):
    uuid: UUID4
    token: Annotated[str, Indexed(unique=True)]
    created_at: Annotated[datetime, Indexed(expireAfterSeconds=60 * 60)]


class UserConfig(BaseModel):
    """User configuration model storing the same data the mod stores locally

    Any provided key-value pairs not in this model will be ignored by the server when pushing an
    update to a player's settings. Similarly, any keys not provided will revert to their
    default values.

    Note that the server does not validate the allowed range for any number values; any clients
    consuming this data should ensure that they restrict any received values to the relevant
    allowed ranges.
    """

    # username is intentionally skipped

    ### NOTE TO CONTRIBUTORS: ##
    # All fields below MUST have their default value listed, otherwise things WILL break!

    gender: Gender = Gender.MALE

    bust_size: float = 0.6
    hurt_sounds: bool = True

    breasts_xOffset: float = 0.0
    breasts_yOffset: float = 0.0
    breasts_zOffset: float = 0.0
    breasts_uniboob: bool = True
    breasts_cleavage: float = 0.0

    breast_physics: bool = True
    # armor_physics_override is intentionally skipped
    show_in_armor: bool = True
    bounce_multiplier: float = 0.333
    floppy_multiplier: float = 0.75

    voice_pitch: float = 1.0
    holiday_themes: bool = True

    class Settings:
        use_cache = True
        cache_expiration_time = timedelta(minutes=10)
        cache_capacity = 2048


# TODO these property docstrings are not shown in the generated OpenAPI model docs :(
class ContributorNametag(BaseModel):
    text: str
    """Text displayed instead of the normal contributor nametag.

    This value is ignored on versions that support ``roles``, but is still required
    for backwards compatibility with versions that do not support it."""

    name: str | None = None
    """Optional; the contributor's display name. This does not have to match the username of the
    associated Minecraft account.

    This must be set for a contributor to be displayed in the in-game credits screen."""

    color: int | None = None
    """"Optional; packed RGB color used for the nametag above a contributor's head, and in various other UIs.

    This may be null to use the regular contributor color."""

    roles: int | None = None
    """Bitmask referring to the following possible enum values (in the following order):

    - MOD_CREATOR
    - FABRIC_MAINTAINER
    - NEOFORGE_MAINTAINER
    - DEVELOPER
    - TRANSLATOR
    - MASCOT
    - GENERIC"""

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
