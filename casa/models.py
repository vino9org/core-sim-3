import enum

from tortoise.fields import CharEnumField, CharField, DatetimeField, DecimalField, IntField
from tortoise.models import Model


class StatusEnum(enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class AccountModel(Model):
    id = IntField(primary_key=True)
    account_num = CharField(max_length=16)
    currency = CharField(max_length=20, default="USD")
    balance = DecimalField(max_digits=14, decimal_places=2)
    updated_at = DatetimeField(auto_now_add=True)
    status = CharEnumField(enum_type=StatusEnum, default=StatusEnum.ACTIVE)

    class Meta:
        table = "casa_account"
