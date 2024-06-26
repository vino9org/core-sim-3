import logging

import pytest

from app import app

# suppress INFO logs to reduce noise in test output
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARN)


@pytest.fixture
async def client():
    async with app.test_client() as client:
        yield client
