import logging
from datetime import datetime

import ulid

from . import schemas

__ALL__ = ["get_account_details", "transfer", "InvalidRequest"]


logger = logging.getLogger(__name__)


class InvalidRequest(Exception):
    pass


async def get_account_details(account_num: str) -> schemas.AccountSchema | None:
    if account_num == "bad_account":
        return None

    logger.info("Getting account details for %s", account_num)

    return schemas.AccountSchema(
        account_num=account_num,
        currency="USD",
        balance=100.00,
        avail_balance=100.00,
        status="ACTIVE",
        updated_at=datetime.now(),
    )


async def transfer(transfer: schemas.TransferSchema) -> schemas.TransferSchema:
    if transfer.credit_account_num == "bad_account":
        raise InvalidRequest("Invalid transaction date")

    transfer.trx_id = ulid.new().str
    return transfer
