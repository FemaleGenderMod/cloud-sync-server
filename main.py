import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.responses import PlainTextResponse, RedirectResponse, Response

from core import util
from core.common_models import StatsResponse
from core.db import init_db, User
from routes import v1, v2, admin


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
    license_info={"name": "AGPL-3.0", "identifier": "AGPL-3.0-only"},
    description="""Sync server for the [Female Gender Mod](https://modrinth.com/mod/female-gender)

Available versions:
- [v1](/v1/docs) (deprecated)
- [v2](/v2/docs)
""",
)
app.mount("/v1", v1.app)
app.mount("/v2", v2.app)
app.mount("/admin", admin.app)


@app.get("/", include_in_schema=False)
def redirect_root():
    return RedirectResponse("https://modrinth.com/mod/female-gender")


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
