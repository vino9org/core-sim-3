from typing import Annotated, TypeAlias

from annotated_types import Gt
from pydantic import BaseModel, constr
from tortoise.contrib.pydantic import pydantic_model_creator

from .models import AccountModel, TransferModel

positive: TypeAlias = Annotated[float, Gt(0)]
curreny: TypeAlias = Annotated[str, constr(min_length=3, max_length=3)]

Account = pydantic_model_creator(
    AccountModel,
    name="Account",
    exclude=("id",),
)

Transfer = pydantic_model_creator(
    TransferModel,
    name="Transfer",
    exclude=("id",),
)


class TransferRequest(BaseModel):
    ref_id: str
    trx_date: str
    debit_account_num: str
    credit_account_num: str
    currency: curreny
    amount: positive
    memo: str
