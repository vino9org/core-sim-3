from casa import models as m


async def test_query_account(test_db):
    model = await m.AccountModel.filter(account_num="1234567890").first()
    assert model
    assert model.account_num == "1234567890"
