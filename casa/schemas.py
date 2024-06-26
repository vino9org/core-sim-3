from tortoise.contrib.pydantic import pydantic_model_creator

from .models import AccountModel

Account = pydantic_model_creator(
    AccountModel,
    name="Account",
    exclude=("id",),
)
