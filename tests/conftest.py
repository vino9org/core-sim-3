import asyncio
import logging
import os
from datetime import datetime
from uuid import uuid4

import pytest
import tortoise.contrib.test as tortoise_test
import ulid
from tortoise import Tortoise

# from tortoise.contrib.test import _init_db, getDBConfig
from app import app
from casa.models import AccountModel, TransactionModel, TransferModel

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
    test_db_url = os.environ.get("TEST_DATABASE_URL", "sqlite://:memory:")
    tortoise_test._TORTOISE_TEST_DB = test_db_url
    config = tortoise_test.getDBConfig(app_label="models", modules=["casa.models"])
    event_loop.run_until_complete(tortoise_test._init_db(config))
    event_loop.run_until_complete(seed_db())

    if os.environ.get("KEEP_TEST_DB", "N").upper() not in ["Y", "1"]:
        request.addfinalizer(lambda: event_loop.run_until_complete(Tortoise._drop_databases()))


async def seed_db():
    # seed the database with some test data
    today = datetime.now().strftime("%Y-%m-%d")
    account1 = await AccountModel.create(
        account_num="1234567890",
        currency="USD",
        balance=1000.00,
        avail_balance=1000.00,
    )
    account2 = await AccountModel.create(
        account_num="0987654321",
        currency="USD",
        balance=500.00,
        avail_balance=500.00,
    )

    ref_id = uuid4().hex
    trx_id = ulid.new().str

    await TransactionModel.create(
        trx_id=trx_id,
        ref_id=ref_id,
        trx_date=today,
        currency="USD",
        amount=100.00,
        memo="gift",
        account=account1,
        running_balance=1000.00,
    )

    await TransactionModel.create(
        trx_id=trx_id,
        ref_id=ref_id,
        trx_date=today,
        currency="USD",
        amount=100.00,
        memo=f"From {account1.account_num}: gift",
        account=account2,
        running_balance=500.00,
    )

    await TransferModel.create(
        trx_id=trx_id,
        ref_id=ref_id,
        trx_date=today,
        currency="USD",
        amount=100.00,
        memo="gift",
        debit_account_num=account1.account_num,
        credit_account_num=account2.account_num,
    )
