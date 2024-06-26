import logging

from tortoise.contrib.pydantic import PydanticModel

from . import models as m
from . import schemas as s

__ALL__ = ["get_account_details", "transfer", "InvalidRequest"]


logger = logging.getLogger(__name__)


class InvalidRequest(Exception):
    pass


async def get_account_details(account_num: str) -> PydanticModel | None:
    model = await m.AccountModel.filter(account_num=account_num).first()
    return await s.Account.from_tortoise_orm(model) if model else None
