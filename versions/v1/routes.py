from typing import Annotated

from beanie.odm.operators.find.comparison import In
from fastapi import FastAPI, Query, Header
from pydantic import UUID4
from starlette.responses import Response, PlainTextResponse, JSONResponse

import core.auth
from core.common_models import ErrorResponse, AuthenticatedResponse, SuccessResponse
from core.db import UserConfig, User, ContributorNametag

__all__ = (
    "app",
    "get_auth",
    "get_multiple_players",
    "contributors",
    "get_player",
    "delete_data",
    "update_data",
)

from .models import BulkQueryResponse, UserData

app = FastAPI(
    description="**This API version is deprecated; please use [v2](/v2/docs) instead if possible.**",
    version="1.0.0",
)


# if only QUERY wasn't still a draft...
@app.post(
    "/",
    response_model=BulkQueryResponse,
    responses={400: {"model": ErrorResponse}},
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
        "users": {
            x.uuid: UserData.from_db(x.data)
            async for x in User.find_many(In(User.uuid, body))
            if x.data
        },
    }


@app.get(
    "/contributors",
    response_model=dict[UUID4, ContributorNametag],
    summary="Get contributor nametags",
)
async def contributors(response: Response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    # noinspection PyComparisonWithNone
    return {x.uuid: x.nametag async for x in User.find(User.nametag != None)}


@app.get(
    "/auth",
    response_model=AuthenticatedResponse,
    responses={
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Get authentication token",
)
async def get_auth(
    server_id: Annotated[str, Query(alias="serverId")],
    username: Annotated[str, Query()],
    response: Response,
):
    """Retrieve an authentication token used for updating player data

    This route requires [authenticating with Mojang's session servers](https://minecraft.wiki/w/Java_Edition_protocol/Encryption#Authentication).

    The provided authentication token will expire after 1 hour, and will automatically be invalidated if
    this route is called again before it expires.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return await core.auth.handle_auth_request(server_id, username)


# NOTE: the following routes MUST be the last routes; any additional top-level routes added
# after this will be shadowed by the player endpoint routes, and will not be resolved correctly.


@app.put(
    "/{uuid}",
    response_model=SuccessResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Update player data",
)
async def update_data(uuid: UUID4, auth_token: Annotated[str, Header()], body: UserData):
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
    "/{uuid}",
    responses={
        204: {},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
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

    if user.nametag:
        await user.set({User.data: None})
    else:
        await user.delete()

    return PlainTextResponse(status_code=204)


@app.get("/{uuid}", response_model=UserConfig, responses={204: {}}, summary="Get player data")
async def get_player(uuid: UUID4, response: Response):
    """Returns data for the given player if any data exists"""
    response.headers["Cache-Control"] = "public,max-age=600"
    user = await User.find_one(User.uuid == uuid)
    return user and UserData.from_db(user.data) or PlainTextResponse(status_code=204)
