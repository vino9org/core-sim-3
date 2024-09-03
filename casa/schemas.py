from typing import Annotated, TypeAlias

from annotated_types import Gt
from pydantic import BaseModel, constr
from tortoise.contrib.pydantic import pydantic_model_creator

from .models import AccountModel, TransferModel

positive: TypeAlias = Annotated[float, Gt(0)]
currency: TypeAlias = Annotated[str, constr(min_length=3, max_length=3)]
trxdate: TypeAlias = Annotated[str, constr(pattern=r"^\d{4}-\d{2}-\d{2}$")]

Account = pydantic_model_creator(
    AccountModel,
    name="Account",
    exclude=("id", "updated_at"),
)


Transfer = pydantic_model_creator(
    TransferModel,
    name="Transfer",
    exclude=("id", "created_at"),
)


class TransferRequest(BaseModel):
    ref_id: str
    trx_date: trxdate
    debit_account_num: str
    credit_account_num: str
    currency: currency
    amount: positive
    memo: str
