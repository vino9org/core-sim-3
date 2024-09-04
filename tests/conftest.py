import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncGenerator
from uuid import uuid4

import pytest
import ulid
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tortoise import Tortoise
from tortoise.contrib.fastapi import RegisterTortoise
from tortoise.exceptions import OperationalError

from casa import models as m

# suppress INFO logs to reduce noise in test output
# root_logger = logging.getLogger()
# root_logger.setLevel(logging.WARN)


async def _seed_db():
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


#
# database utilites
#


def test_db_path():
    test_db_path = Path(__name__).parent / "tmp"
    test_db_path.mkdir(parents=True, exist_ok=True)
    return f"{test_db_path.resolve()}/test.db"


async def _prep_test_db() -> dict[str, Any]:
    from main import TORTOISE_CONF

    conf = TORTOISE_CONF.copy()
    conf["connections"]["default"] = os.environ.get(
        "TEST_DATABASE_URL",
        f"sqlite://{test_db_path()}",
    )

    print("*** _prep_test_db ***")
    try:
        await Tortoise.init(conf, _create_db=True)
        await Tortoise.generate_schemas(safe=False)
        await _seed_db()
    except OperationalError as e:
        # database already exists
        if "already exists" in str(e):
            await Tortoise.init(conf, _create_db=False)

    return conf


async def _cleanup_test_db():
    if os.environ.get("KEEP_TEST_DB", "N").upper() not in ["Y", "1"]:
        await Tortoise._drop_databases()


#
# FastAPI lifespan context manager
#
@asynccontextmanager
async def lifespan_test(app: FastAPI) -> AsyncGenerator[None, None]:
    print("**** lifespan_test ****")
    conf = await _prep_test_db()

    async with RegisterTortoise(
        app,
        config=conf,
        generate_schemas=False,
    ):
        yield

    await _cleanup_test_db()


#
# fixtures
#
@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db(event_loop):
    event_loop.run_until_complete(_prep_test_db())
    yield
    event_loop.run_until_complete(_cleanup_test_db())


@pytest.fixture(scope="session")
async def client():
    from main import app

    app.router.lifespan_context = lifespan_test
    with TestClient(app) as client:
        yield client
