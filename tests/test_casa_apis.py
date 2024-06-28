from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from casa import models as m


async def test_get_account_details(client, test_db):
    response = await client.get("/api/casa/accounts/1234567890")
    assert response.status_code == 200
    body = await response.json
    assert body["currency"] == "USD"
    assert body["balance"] == float("1000.00")


async def test_get_account_not_found(client, test_db):
    response = await client.get("/api/casa/accounts/bad_account")
    assert response.status_code == 404


async def test_transfer_success(client, mocker, test_db):
    debit_account_num = "0987654321"
    credit_account_num = "1234567890"
    amount = 15.0

    payload = {
        "ref_id": uuid4().hex,
        "trx_date": datetime.now().strftime("%Y-%m-%d"),
        "debit_account_num": debit_account_num,
        "credit_account_num": credit_account_num,
        "currency": "USD",
        "amount": amount,
        "memo": "test transfer",
    }

    debit_account_before = (
        await m.AccountModel.filter(account_num=debit_account_num).prefetch_related("transactions").first()
    )
    credit_account_before = (
        await m.AccountModel.filter(account_num=credit_account_num).prefetch_related("transactions").first()
    )
    assert debit_account_before
    assert credit_account_before

    mock = mocker.patch("casa.api.service.publish_events")
    response = await client.post("/api/casa/transfers", json=payload)

    debit_account_after = (
        await m.AccountModel.filter(account_num=debit_account_num).prefetch_related("transactions").first()
    )
    credit_account_after = (
        await m.AccountModel.filter(account_num=credit_account_num).prefetch_related("transactions").first()
    )
    assert debit_account_after
    assert credit_account_after

    assert response.status_code == 201
    body = await response.json

    assert body["trx_id"]
    assert body["amount"] == float("15.00")
    assert (debit_account_before.balance - debit_account_after.balance) == Decimal(amount)
    assert (credit_account_after.balance - credit_account_before.balance) == Decimal(amount)
    assert len(credit_account_after.transactions) == len(credit_account_before.transactions) + 1
    assert len(debit_account_after.transactions) == len(credit_account_before.transactions) + 1

    mock.assert_called_once()
    args, _ = mock.call_args
    assert len(args[0]) == 2
    assert issubclass(m.TransactionModel, args[0][0][0])


async def test_transfer_with_bad_account(client, test_db):
    # payload with all required fields but invalid account number
    payload = {
        "ref_id": uuid4().hex,
        "trx_date": "2021-01-02",
        "debit_account_num": "0987654321",
        "credit_account_num": "bad_account",
        "currency": "USD",
        "amount": 15.00,
        "memo": "test transfer",
    }

    response = await client.post("/api/casa/transfers", json=payload)
    assert response.status_code == 422


async def test_transfer_incomplete_request(client, test_db):
    # payload incomplete, trx_date is required field but not supplied
    payload = {
        "debit_account_num": "0987654321",
        "credit_account_num": "bad_account",
        "currency": "USD",
        "amount": 15.00,
        "memo": "test transfer",
    }

    response = await client.post("/api/casa/transfers", json=payload)
    assert response.status_code == 422
