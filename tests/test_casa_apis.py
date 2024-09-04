from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from casa import models as m


async def test_get_account_details(client):
    response = client.get("/api/casa/accounts/1234567890")
    assert response.status_code == 200
    body = response.json()
    assert body["currency"] == "USD"
    assert Decimal(body["balance"]) == Decimal("1000.00")


async def test_get_account_not_found(client):
    response = client.get("/api/casa/accounts/bad_account")
    assert response.status_code == 404


async def test_transfer_success(client, mocker):
    debit_account_num = "0987654321"
    credit_account_num = "1234567890"
    amount = Decimal("15.01")

    payload = {
        "ref_id": uuid4().hex,
        "trx_date": datetime.now().strftime("%Y-%m-%d"),
        "debit_account_num": debit_account_num,
        "credit_account_num": credit_account_num,
        "currency": "USD",
        "amount": str(amount),
        "memo": "test transfer",
    }

    debit_before = (
        await m.AccountModel.filter(account_num=debit_account_num)
        .prefetch_related("transactions")
        .first()
    )
    credit_before = (
        await m.AccountModel.filter(account_num=credit_account_num)
        .prefetch_related("transactions")
        .first()
    )
    assert debit_before
    assert credit_before

    mock = mocker.patch("casa.api.service.publish_events")
    response = client.post("/api/casa/transfers", json=payload)

    debit_after = (
        await m.AccountModel.filter(account_num=debit_account_num)
        .prefetch_related("transactions")
        .first()
    )
    credit_after = (
        await m.AccountModel.filter(account_num=credit_account_num)
        .prefetch_related("transactions")
        .first()
    )
    assert debit_after
    assert credit_after

    assert response.status_code == 201
    body = response.json()

    assert body["trx_id"]
    assert Decimal(body["amount"]) == amount
    assert (debit_before.balance - debit_after.balance) == Decimal(amount)
    assert (credit_after.balance - credit_before.balance) == Decimal(amount)
    assert len(credit_after.transactions) == len(credit_before.transactions) + 1
    assert len(debit_after.transactions) == len(credit_before.transactions) + 1

    mock.assert_called_once()
    args, _ = mock.call_args
    assert len(args[0]) == 2
    assert isinstance(args[0][0], m.TransactionModel)


async def test_transfer_with_bad_account(client):
    # payload with all required fields but invalid account number
    payload = {
        "ref_id": uuid4().hex,
        "trx_date": "2021-01-02",
        "debit_account_num": "0987654321",
        "credit_account_num": "bad_account",
        "currency": "USD",
        "amount": "15.00",
        "memo": "test transfer",
    }

    response = client.post("/api/casa/transfers", json=payload)
    assert response.status_code == 422


async def test_transfer_incomplete_request(client):
    # payload incomplete, trx_date is required field but not supplied
    payload = {
        "debit_account_num": "0987654321",
        "credit_account_num": "bad_account",
        "currency": "USD",
        "amount": "15.00",
        "memo": "test transfer",
    }

    response = client.post("/api/casa/transfers", json=payload)
    assert response.status_code == 422
