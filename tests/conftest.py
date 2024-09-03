import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator
from uuid import uuid4

import pytest
import ulid
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tortoise import Tortoise
from tortoise.contrib.fastapi import RegisterTortoise

from casa import models as m
from main import app, lifespan, tortoise_conf

# suppress INFO logs to reduce noise in test output
root_logger = logging.getLogger()
root_logger.setLevel(logging.WARN)


@asynccontextmanager
async def lifespan_test(app: FastAPI) -> AsyncGenerator[None, None]:
    test_databae_url = os.environ.get("TEST_DATABASE_URL", "sqlite://:memory:")
    async with RegisterTortoise(
        app,
        config=tortoise_conf(app, test_databae_url),
        generate_schemas=False,
    ):
        yield
        await Tortoise.close_connections()


app.dependency_overrides[lifespan] = lifespan_test


@pytest.fixture(scope="session")
async def client():
    yield TestClient(app)


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
    import tortoise.contrib.test as tortoise_test

    test_db_url = os.environ.get("TEST_DATABASE_URL", "sqlite://:memory:")
    tortoise_test._TORTOISE_TEST_DB = test_db_url
    config = tortoise_test.getDBConfig(app_label="models", modules=["casa.models"])
    event_loop.run_until_complete(tortoise_test._init_db(config))
    event_loop.run_until_complete(seed_db())

    yield

    if os.environ.get("KEEP_TEST_DB", "N").upper() not in ["Y", "1"]:
        event_loop.run_until_complete(Tortoise._drop_databases())


async def seed_db():
    # seed the database with some test data
    today = datetime.now().strftime("%Y-%m-%d")
    account1 = await m.AccountModel.create(
        account_num="1234567890",
        currency="USD",
        balance=1000.00,
        avail_balance=1000.00,
    )
    account2 = await m.AccountModel.create(
        account_num="0987654321",
        currency="USD",
        balance=500.00,
        avail_balance=500.00,
    )

    ref_id = uuid4().hex
    trx_id = ulid.new().str

    await m.TransactionModel.create(
        trx_id=trx_id,
        ref_id=ref_id,
        trx_date=today,
        currency="USD",
        amount=100.00,
        memo="gift",
        account=account1,
        running_balance=1000.00,
    )

    await m.TransactionModel.create(
        trx_id=trx_id,
        ref_id=ref_id,
        trx_date=today,
        currency="USD",
        amount=100.00,
        memo=f"From {account1.account_num}: gift",
        account=account2,
        running_balance=500.00,
    )

    await m.TransferModel.create(
        trx_id=trx_id,
        ref_id=ref_id,
        trx_date=today,
        currency="USD",
        amount=100.00,
        memo="gift",
        debit_account_num=account1.account_num,
        credit_account_num=account2.account_num,
    )
