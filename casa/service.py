import logging
from decimal import Decimal
from typing import Type

import ulid
from tortoise.contrib.pydantic import PydanticModel
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from . import models as m
from . import schemas as s

__ALL__ = ["get_account_details", "transfer", "InvalidRequest", "publish_events"]


logger = logging.getLogger(__name__)


class InvalidRequest(Exception):
    pass


async def get_account_details(account_num: str) -> PydanticModel | None:
    model = await m.AccountModel.filter(account_num=account_num).first()
    return await s.Account.from_tortoise_orm(model) if model else None


async def _lock_accounts_for_transfer_(
    conn,
    debit_account_num: str,
    credit_account_num: str,
) -> tuple[m.AccountModel, m.AccountModel]:
    accounts = (
        await m.AccountModel.filter(
            Q(account_num=debit_account_num) | Q(account_num=credit_account_num), status=m.StatusEnum.ACTIVE
        )
        .select_for_update()
        .all()
        .using_db(conn)
    )

    if len(accounts) != 2:
        raise InvalidRequest("Invalid debit or credit account number")

    if accounts[0].account_num == debit_account_num:
        debit_account, credit_account = accounts[0], accounts[1]
    else:
        debit_account, credit_account = accounts[1], accounts[0]

    return debit_account, credit_account


async def transfer(
    transfer_req: s.TransferRequest,
) -> tuple[PydanticModel, list[tuple[Type[m.TransactionModel], int]]]:
    """
    perform a transfer and returns:
    1. transfer object
    2. list of Transfer objects and their id (to be used to event publishing later)
    """
    amount = Decimal(transfer_req.amount)
    debit_account_num = transfer_req.debit_account_num
    credit_account_num = transfer_req.credit_account_num
    ref_id = transfer_req.ref_id
    trx_date = transfer_req.trx_date
    currency = transfer_req.currency
    memo = transfer_req.memo

    async with in_transaction() as conn:
        debit_account, credit_account = await _lock_accounts_for_transfer_(
            conn,
            debit_account_num,
            credit_account_num,
        )
        if debit_account.avail_balance < amount:
            raise InvalidRequest("Insufficient funds in debit account")

        trx_id = str(ulid.new())

        debit_account_balance = debit_account.balance - amount
        debit_account.avail_balance = debit_account_balance
        debit_account.balance = debit_account_balance

        credit_account_balance = credit_account.balance + amount
        credit_account.avail_balance = credit_account_balance
        credit_account.balance = credit_account_balance

        debit_transction = await m.TransactionModel.create(
            ref_id=ref_id,
            trx_date=trx_date,
            trx_id=trx_id,
            currency=currency,
            amount=-amount,
            memo=memo,
            account=debit_account,
            running_balance=debit_account_balance,
        )

        credit_transction = await m.TransactionModel.create(
            ref_id=ref_id,
            trx_date=trx_date,
            trx_id=trx_id,
            currency=currency,
            amount=amount,
            memo=f"from {debit_account_num}: {memo}",
            account=credit_account,
            running_balance=credit_account_balance,
        )

        transfer_model = await m.TransferModel.create(
            trx_id=trx_id,
            ref_id=ref_id,
            trx_date=trx_date,
            currency=currency,
            amount=amount,
            memo=memo,
            debit_account_num=debit_account_num,
            credit_account_num=credit_account_num,
            using_db=conn,
        )

        result = await s.Transfer.from_tortoise_orm(transfer_model)
        events = [
            (m.TransactionModel, credit_transction.id),
            (m.TransactionModel, debit_transction.id),
        ]

        return result, events


def publish_events(events: list[tuple[Type[m.ModelT], int]]) -> int:
    for e in events:
        msg = f"publishing event for {e[0].__name__}({e[1]})"
        logger.debug(msg)
    return len(events)
