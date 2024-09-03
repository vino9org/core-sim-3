import json
import logging
import logging.config
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

import uvicorn.logging
from dotenv import load_dotenv
from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise

from casa.api import router as casa_router

load_dotenv()

access_log_format: str = ""

with open(Path(__file__).parent / "logger_config.json", "r") as f:
    config = json.load(f)
    access_log_format = config["formatters"]["standard"]["format"]
    logging.config.dictConfig(config)


def patch_unvicorn_logger():
    global access_log_format

    logger = logging.getLogger("uvicorn.access")
    # the uvicorn.logging is out exposed to the public
    # we tell mypy to ignore it for now
    console_formatter = uvicorn.logging.ColourizedFormatter(access_log_format)
    logger.handlers[0].setFormatter(console_formatter)


def tortoise_conf(app: FastAPI, databae_url: str = "") -> dict[str, Any]:
    if not databae_url:
        databae_url = os.environ.get("DATABASE_URL", "")
        if not databae_url:
            raise ValueError("DATABASE_URL not set properly")

    return {
        "connections": {"default": databae_url},
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
        config=tortoise_conf(app),
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
