import asyncio
import logging
import os

import pytest
from tortoise.contrib.test import finalizer, initializer

from app import app
from casa.models import AccountModel  # noqa

# suppress INFO logs to reduce noise in test output
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARN)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    db_url = os.environ.get("TEST_DATABASE_URL", "sqlite://:memory:")
    initializer(["casa.models"], db_url=db_url, app_label="default")
    request.addfinalizer(finalizer)


@pytest.fixture
async def client():
    async with app.test_client() as client:
        yield client
