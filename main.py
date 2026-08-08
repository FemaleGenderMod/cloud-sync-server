import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.params import Header
from pydantic import UUID4
from starlette.responses import JSONResponse, PlainTextResponse, RedirectResponse, Response

from core import util
from core.common_models import SuccessResponse, ErrorResponse, StatsResponse
from db import init_db, UserConfig, User, ContributorNametag
from versions import v1, v2

# this is defined later
# noinspection PyTypeChecker
SESSION: aiohttp.ClientSession = ...


@asynccontextmanager
async def lifecycle(_):
    util.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=4))
    load_dotenv()
    await init_db()

    if os.environ.get("ENABLE_REQUEST_LOGGING", "false") != "true":
        logging.getLogger("uvicorn.access").disabled = True

    yield

    await util.session.close()


app = FastAPI(
    lifespan=lifecycle,
    version=v2.app.version,
    description="""Sync server for the [Female Gender Mod](https://modrinth.com/mod/female-gender)

Available versions:
- [v1](/v1/docs) (deprecated)
- [v2](/v2/docs)
""",
)
app.mount("/v1", v1.app)
app.mount("/v2", v2.app)


@app.get("/", include_in_schema=False)
def redirect_root():
    return RedirectResponse("https://modrinth.com/mod/female-gender")


@app.put(
    "/contributor/{uuid}",
    response_model=SuccessResponse,
    responses={401: {}},
    summary="Update contributor nametag",
)
async def update_contributor(
    uuid: UUID4, auth_token: Annotated[str, Header()], body: ContributorNametag, response: Response
):
    """Internal endpoint, updates the nametag stored for a contributor"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    if auth_token != os.environ["ADMIN_TOKEN"]:
        return PlainTextResponse(status_code=401)

    user = await User.find_one(User.uuid == uuid)
    if user is None:
        user = User(uuid=uuid, data=UserConfig())
        # noinspection PyArgumentList
        await user.insert()
    await user.set({User.nametag: body})

    return {"success": True}


@app.delete(
    "/contributor/{uuid}",
    response_model=SuccessResponse,
    responses={401: {}, 404: {"model": ErrorResponse}},
    summary="Delete contributor nametag",
)
async def delete_contributor(uuid: UUID4, auth_token: Annotated[str, Header()], response: Response):
    """Internal endpoint, deletes any nametag stored for a contributor"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    if auth_token != os.environ["ADMIN_TOKEN"]:
        return PlainTextResponse(status_code=401)

    user = await User.find_one(User.uuid == uuid)
    if user is None:
        return JSONResponse(
            status_code=404, content={"success": False, "error": "No such user exists"}
        )
    await user.set({User.nametag: None})

    return {"success": True}


@app.get("/stats", response_model=StatsResponse, summary="Get sync server statistics")
async def stats(response: Response):
    response.headers["Cache-Control"] = "public, max-age=1800"
    return {"synced_users": await User.count(), "timestamp": datetime.now(timezone.utc)}


@app.get("/health-check", include_in_schema=False)
async def healthcheck(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return PlainTextResponse(status_code=204)


# these are kept for compatibility with older versions
app.post("/", include_in_schema=False)(v1.get_multiple_players)
app.get("/auth", include_in_schema=False)(v1.get_auth)
app.get("/contributors", include_in_schema=False)(v1.contributors)
# these routes must be last
app.get("/{uuid}", include_in_schema=False)(v1.get_player)
app.put("/{uuid}", include_in_schema=False)(v1.update_data)
app.delete("/{uuid}", include_in_schema=False)(v1.delete_data)
