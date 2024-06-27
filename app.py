import json
import logging
import logging.config
import os
from pathlib import Path

from dotenv import load_dotenv
from flask_orjson import OrjsonProvider
from quart import Quart
from tortoise.contrib.quart import register_tortoise

from casa.api import blueprint as casa_api
from casa.models import AccountModel  # noqa

load_dotenv()

with open(Path(__file__).parent / "logger_config.json", "r") as f:
    logging.config.dictConfig(json.load(f))


app = Quart(__name__)
app.json = OrjsonProvider(app)


@app.get("/healthz")
async def health():
    return "running"


@app.get("/ready")
async def ready():
    return "ready"


app.register_blueprint(casa_api, url_prefix="/api/casa")

register_tortoise(
    app,
    db_url=os.environ.get("DATABASE_URL"),
    modules={"models": ["casa.models"]},
    generate_schemas=False,
)


if __name__ == "__main__":
    app.run(port=8000)
