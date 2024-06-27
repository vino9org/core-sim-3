from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "casa_account" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "account_num" VARCHAR(16) NOT NULL,
    "currency" VARCHAR(20) NOT NULL  DEFAULT 'USD',
    "balance" DECIMAL(14,2) NOT NULL,
    "avail_balance" DECIMAL(14,2) NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "status" VARCHAR(9) NOT NULL  DEFAULT 'ACTIVE'
);
CREATE INDEX IF NOT EXISTS "idx_casa_accoun_account_995004" ON "casa_account" ("account_num", "status");
COMMENT ON COLUMN "casa_account"."status" IS 'ACTIVE: ACTIVE\nSUSPENDED: SUSPENDED\nCLOSED: CLOSED';
CREATE TABLE IF NOT EXISTS "casa_transaction" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "trx_date" VARCHAR(10) NOT NULL,
    "currency" VARCHAR(3) NOT NULL,
    "amount" DECIMAL(14,2) NOT NULL,
    "running_balance" DECIMAL(14,2) NOT NULL,
    "ref_id" VARCHAR(32) NOT NULL,
    "memo" VARCHAR(100) NOT NULL,
    "is_published" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "account_id" INT NOT NULL REFERENCES "casa_account" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_casa_transa_trx_dat_4e1bca" ON "casa_transaction" ("trx_date");
CREATE INDEX IF NOT EXISTS "idx_casa_transa_account_a26973" ON "casa_transaction" ("account_id", "trx_date");
CREATE TABLE IF NOT EXISTS "casa_transfer" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "trx_id" VARCHAR(32) NOT NULL UNIQUE,
    "trx_date" VARCHAR(10) NOT NULL,
    "currency" VARCHAR(3) NOT NULL,
    "amount" DECIMAL(14,2) NOT NULL,
    "ref_id" VARCHAR(32) NOT NULL,
    "memo" VARCHAR(100) NOT NULL,
    "debit_account_num" VARCHAR(32) NOT NULL,
    "credit_account_num" VARCHAR(32) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_casa_transf_trx_dat_dce497" ON "casa_transfer" ("trx_date");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
