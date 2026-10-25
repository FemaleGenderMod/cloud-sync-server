from typing import Annotated

from beanie.odm.operators.find.comparison import In
from fastapi import FastAPI, Header
from pydantic import UUID4
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse, JSONResponse

import core.auth
from core.common_models import AuthenticatedResponse, ErrorResponse, SuccessResponse
from core.db import User
from core.util import limiter
from .models import AuthenticationBody, UserData, BulkQueryResponse

app = FastAPI(version="2.0.0")


# request is required for @limiter.limit
# noinspection PyUnusedLocal
@app.post(
    "/auth",
    response_model=AuthenticatedResponse,
    responses={
        403: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    summary="Authenticate with Mojang",
)
# relatively strict rate limit as you ideally shouldn't be authenticating this often to begin with
@limiter.limit("10/hour")
async def authenticate(body: AuthenticationBody, request: Request):
    """Retrieve an authentication token used for updating player data

    This route requires [authenticating with Mojang's session servers](https://minecraft.wiki/w/Java_Edition_protocol/Encryption#Authentication).

    The provided authentication token will expire after 1 hour, and will automatically be invalidated if
    this route is called again before it expires.
    """
    return await core.auth.handle_auth_request(body.server_id, body.username)


@app.get(
    "/contributors",
    response_model=dict,
    summary="Get contributor nametags",
    deprecated=True,
)
async def contributors(response: Response):
    """
    Deprecated; the relevant mod feature that used this has been removed, and as such this route no longer returns any data.
    """
    response.headers["Cache-Control"] = "public, max-age=21600"
    return {}


# would still love to be able to use QUERY :(
@app.post(
    "/players",
    response_model=BulkQueryResponse,
    responses={
        400: {"model": ErrorResponse},
    },
    summary="Get data for multiple players",
)
async def get_multiple_players(body: set[UUID4]):
    """Get player data for up to 20 unique UUIDs at once

    Any provided UUIDs that the server doesn't have any sync data for will simply be omitted from
    the returned users object.
    """
    if len(body) < 2:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "This route requires at least 2 unique UUIDs to be provided",
            },
        )
    if len(body) > 20:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Bulk queries have a limit of 20 unique UUIDs at once",
            },
        )

    return {
        "success": True,
        "users": {x.uuid: UserData.from_db(x.data) async for x in User.find_many(In(User.uuid, body)) if x.data},
    }


@app.get(
    "/player/{uuid}",
    response_model=UserData,
    responses={
        204: {},
    },
    summary="Get player data",
)
async def get_player(uuid: UUID4, response: Response):
    """Returns data for the given player if any data exists"""
    response.headers["Cache-Control"] = "public,max-age=600"
    user = await User.find_one(User.uuid == uuid)
    return user and UserData.from_db(user.data) or PlainTextResponse(status_code=204)


@app.put(
    "/player/{uuid}",
    response_model=SuccessResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Update player data",
)
async def update_player(uuid: UUID4, auth_token: Annotated[str, Header()], body: UserData):
    """Stores the provided player data for the given authenticated user

    This requires an `Auth-Token` header provided from the `/auth` route.
    """
    auth = await core.auth.authenticate(auth_token, uuid)
    if auth.error:
        return auth.error

    user = await User.find_one_or_create(uuid)
    user.data = body.to_db()
    await user.save()
    return {"success": True}


@app.delete(
    "/player/{uuid}",
    responses={
        204: {},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Delete player data",
)
async def delete_data(uuid: UUID4, auth_token: Annotated[str, Header()]):
    """Deletes the stored player data for the given authenticated user

    This requires an `Auth-Token` header provided from the `/auth` route.

    Note that the provided authentication token remains valid for its normal lifecycle after
    sending a request to this route.
    """
    auth = await core.auth.authenticate(auth_token, uuid)
    if auth.error:
        return auth.error

    user = await User.find_one({User.uuid: uuid})
    if not user or not user.data:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "No data is stored for the given player"},
        )

    await user.delete()
    return PlainTextResponse(status_code=204)
