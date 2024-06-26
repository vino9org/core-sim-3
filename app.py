import json
import logging
import logging.config

from quart import Quart

from casa.api import blueprint as casa_api

LOGGING_CONFIG = {}
with open("logger_config.json", "r") as f:
    LOGGING_CONFIG = json.load(f)
    logging.config.dictConfig(LOGGING_CONFIG)

app = Quart("core-sim")


@app.get("/healthz")
async def health():
    return "running"


@app.get("/ready")
async def ready():
    return "ready"


app.register_blueprint(casa_api, url_prefix="/api/casa")


if __name__ == "__main__":
    app.run()
