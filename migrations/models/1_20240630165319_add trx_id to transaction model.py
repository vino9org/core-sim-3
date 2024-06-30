from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "casa_transaction" ADD "trx_id" VARCHAR(32) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "casa_transaction" DROP COLUMN "trx_id";"""
