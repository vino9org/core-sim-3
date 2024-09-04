import json
import logging
import logging.config
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import uvicorn.logging
from dotenv import load_dotenv
from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise

from casa.api import router as casa_router

load_dotenv()

LOGGER_CONFIG = {}

with open(Path(__file__).parent / "logger_config.json", "r") as f:
    LOGGER_CONFIG = json.load(f)
    logging.config.dictConfig(LOGGER_CONFIG)


def patch_unvicorn_logger():
    """patch the uvicorn logger to use the same format as the rest of the app"""
    try:
        logger = logging.getLogger("uvicorn.access")
        # the uvicorn.logging is out exposed to the public
        # we tell mypy to ignore it for now
        console_formatter = uvicorn.logging.ColourizedFormatter(
            LOGGER_CONFIG["formatters"]["standard"]["format"]
        )
        logger.handlers[0].setFormatter(console_formatter)
    except IndexError:
        pass


TORTOISE_CONF = {
    "connections": {"default": os.environ.get("DATABASE_URL", "")},
    "apps": {
        "models": {
            "models": ["casa.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    patch_unvicorn_logger()
    async with RegisterTortoise(
        app,
        config=TORTOISE_CONF,
        generate_schemas=False,
    ):
        yield


app = FastAPI(lifespan=lifespan)
app.include_router(casa_router)


@app.get("/healthz", include_in_schema=False)
async def health():
    return "running"


@app.get("/ready", include_in_schema=False)
async def ready():
    return "ready"


if __name__ == "__main__":
    uvicorn.run(app)
