from casa import models as m


async def test_query_models(test_db):
    account = await m.AccountModel.filter(account_num="1234567890").prefetch_related("transactions").first()
    assert account
    assert account.account_num == "1234567890"
    assert account.transactions[0].running_balance == account.balance
