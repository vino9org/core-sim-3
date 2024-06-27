import enum
from typing import TypeVar

from tortoise import fields as f
from tortoise.fields.base import OnDelete
from tortoise.models import Model

ModelT = TypeVar("ModelT", bound=Model)


class StatusEnum(enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class AccountModel(Model):
    id = f.IntField(primary_key=True)
    account_num = f.CharField(max_length=16)
    currency = f.CharField(max_length=20, default="USD")
    balance = f.DecimalField(max_digits=14, decimal_places=2)
    avail_balance = f.DecimalField(max_digits=14, decimal_places=2)
    updated_at = f.DatetimeField(auto_now_add=True)
    status = f.CharEnumField(enum_type=StatusEnum, default=StatusEnum.ACTIVE)

    transactions: f.ReverseRelation["TransactionModel"]

    class Meta:
        table = "casa_account"
        indexes = [
            ("account_num", "status"),
        ]


class TransactionModel(Model):
    id = f.IntField(primary_key=True)
    trx_date = f.CharField(max_length=10, db_index=True)
    currency = f.CharField(max_length=3)
    amount = f.DecimalField(max_digits=14, decimal_places=2)
    running_balance = f.DecimalField(max_digits=14, decimal_places=2)
    ref_id = f.CharField(max_length=32)
    memo = f.CharField(max_length=100)
    is_published = f.BooleanField(default=False)
    created_at = f.DatetimeField(auto_now_add=True)

    account: f.ForeignKeyRelation[AccountModel] = f.ForeignKeyField(
        "models.AccountModel", related_name="transactions", on_delete=OnDelete.CASCADE
    )

    class Meta:
        table = "casa_transaction"
        indexes = [
            ("account", "trx_date"),
        ]


class TransferModel(Model):
    id = f.IntField(primary_key=True)
    trx_id = f.CharField(max_length=32, unique=True)
    trx_date = f.CharField(max_length=10, db_index=True)
    currency = f.CharField(max_length=3)
    amount = f.DecimalField(max_digits=14, decimal_places=2)
    ref_id = f.CharField(max_length=32)
    memo = f.CharField(max_length=100)
    debit_account_num = f.CharField(max_length=32)
    credit_account_num = f.CharField(max_length=32)
    created_at = f.DatetimeField(auto_now_add=True)

    class Meta:
        table = "casa_transfer"
