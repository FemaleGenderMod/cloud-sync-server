import asyncio
import secrets
from datetime import datetime, timezone, timedelta
from uuid import UUID

from pydantic import UUID4
from starlette.responses import JSONResponse

from db import UserAuth
from . import util


class InvalidAuthenticationError(RuntimeError):
    message: str

    def __init__(self, message: str):
        self.message = message


class AuthServerError(RuntimeError):
    message: str

    def __init__(self, message: str):
        self.message = message


async def validate_session_server(server_id: str, username: str) -> UUID4:
    url = "https://sessionserver.mojang.com/session/minecraft/hasJoined"
    params = {"username": username, "serverId": server_id}
    async with util.session.get(url, params=params) as response:
        if response.status >= 400:
            raise AuthServerError(
                f"Session servers returned an unexpected response status {response.status}"
            )
        json = await response.json()
        if not json or "id" not in json:
            raise InvalidAuthenticationError("Couldn't authenticate with Mojang")
        return UUID(json["id"])


async def handle_auth_request(server_id: str, username: str) -> dict | JSONResponse:
    try:
        uuid = await validate_session_server(server_id, username)
    except AuthServerError as e:
        return JSONResponse(status_code=500, content={"success": False, "error": e.message})
    except InvalidAuthenticationError as e:
        return JSONResponse(status_code=403, content={"success": False, "error": e.message})
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Couldn't reach the authentication servers"},
        )

    await UserAuth.find_many(UserAuth.uuid == uuid).delete_many()
    auth = UserAuth(
        uuid=uuid, token=secrets.token_urlsafe(32), created_at=datetime.now(timezone.utc)
    )
    # noinspection PyArgumentList
    await auth.insert()

    return {
        "success": True,
        "token": auth.token,
        "account": auth.uuid,
        "expires": auth.created_at + timedelta(hours=1),
    }
