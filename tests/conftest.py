import asyncio
import logging
import os

import pytest
from tortoise import Tortoise
from tortoise.backends.base.config_generator import generate_config
from tortoise.contrib.test import _init_db

from app import app
from casa.models import AccountModel  # noqa

# suppress INFO logs to reduce noise in test output
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARN)


@pytest.fixture
async def client():
    async with app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db(request, event_loop):
    config = generate_config(
        os.environ.get("TEST_DATABASE_URL", "sql://:memory:"),
        app_modules={"models": ["casa.models"]},
        testing=True,
        connection_label="models",
    )
    event_loop.run_until_complete(_init_db(config))
    event_loop.run_until_complete(seed_db())

    if os.environ.get("KEEP_TEST_DB", "N").upper() not in ["Y", "1"]:
        request.addfinalizer(lambda: event_loop.run_until_complete(Tortoise._drop_databases()))


async def seed_db():
    # seed the database with some test data
    await AccountModel.create(account_num="1234567890", currency="USD", balance=100.00)
    await AccountModel.create(account_num="0987654321", currency="USD", balance=50.00)
