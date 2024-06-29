import json
import logging
import logging.config
import os
from decimal import Decimal
from pathlib import Path

import orjson
from dotenv import load_dotenv
from flask_orjson import OrjsonProvider
from quart import Quart
from tortoise.contrib.quart import register_tortoise

from casa.api import blueprint as casa_api

load_dotenv()

with open(Path(__file__).parent / "logger_config.json", "r") as f:
    logging.config.dictConfig(json.load(f))


class CustomOrjsonProvider(OrjsonProvider):
    def dumps(self, obj, **kwargs):
        def custom_encoder(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            raise TypeError

        return orjson.dumps(obj, default=custom_encoder).decode()


app = Quart(__name__)
app.json = CustomOrjsonProvider(app)


@app.get("/healthz")
async def health():
    return "running"


@app.get("/ready")
async def ready():
    return "ready"


app.register_blueprint(casa_api, url_prefix="/api/casa")

TORTOISE_ORM = {
    "connections": {"default": os.environ.get("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["casa.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
)


if __name__ == "__main__":
    app.run()
