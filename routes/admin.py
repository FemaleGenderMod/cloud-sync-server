import os
from typing import Annotated

from fastapi import FastAPI, Header
from pydantic import UUID4
from starlette.responses import PlainTextResponse, JSONResponse, Response

from core.common_models import SuccessResponse, ErrorResponse
from core.db import User, ContributorNametag

__all__ = ("app",)
app = FastAPI()


@app.put(
    "/contributor/{uuid}",
    response_model=SuccessResponse,
    responses={401: {}},
    summary="Update contributor nametag",
)
async def update_contributor(
    uuid: UUID4, auth_token: Annotated[str, Header()], body: ContributorNametag, response: Response
):
    """Updates the nametag stored for a contributor"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    if auth_token != os.environ["ADMIN_TOKEN"]:
        return PlainTextResponse(status_code=401)

    user = await User.find_one(User.uuid == uuid)
    if user is None:
        user = User(uuid=uuid, data=None)
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
    """Deletes any nametag stored for a contributor"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    if auth_token != os.environ["ADMIN_TOKEN"]:
        return PlainTextResponse(status_code=401)

    user = await User.find_one(User.uuid == uuid)
    if user is None:
        return JSONResponse(
            status_code=404, content={"success": False, "error": "No such user exists"}
        )
    elif user.data is None:
        await user.delete()
    else:
        await user.set({User.nametag: None})

    return {"success": True}
