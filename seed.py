import argparse
import asyncio
import csv
import os
import random
import sys

from dotenv import load_dotenv
from tortoise import Tortoise

from casa.models import AccountModel, StatusEnum

"""
Utility to create accounts with random balances for load testing
"""

__BALANCE_BUCKETS__ = [100.0, 500.0, 1000.0, 50000.0, 10000000.0]


load_dotenv()


def parse_command_line_options(args):
    parser = argparse.ArgumentParser(description="Generate seed data for load testing")
    parser.add_argument(
        "--truncate",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--mode",
        dest="mode",
        default="load",
        help="load or gen",
    )
    parser.add_argument(
        "--source",
        dest="source",
    )
    parser.add_argument("--output", dest="output", default="-")
    parser.add_argument(
        "--batch",
        dest="batch",
        default=10000,
    )
    parser.add_argument(
        "--count",
        dest="count",
        default=10000,
    )
    parser.add_argument(
        "--start",
        dest="start",
        default=1,
    )

    return parser.parse_args(args)


def generate_csv(file_path: str, count: int, start: int = 1):
    csv_f = sys.stdout if file_path == "-" else open(file_path, "w")
    try:
        writer = csv.DictWriter(
            csv_f,
            fieldnames=["account_num", "currency", "balance"],
        )
        writer.writeheader()

        for i in _gen_random_account_num_(count, 9):
            writer.writerow(
                {
                    "account_num": f"A{i:09}",
                    "currency": "USD",
                    "balance": random.choice(__BALANCE_BUCKETS__),
                }
            )
    finally:
        if csv_f is not sys.stdout:
            csv_f.close()


def _read_csv_(file_path: str, batch_size: int):
    batch = []
    with open(file_path, "r") as csv_f:
        reader = csv.DictReader(csv_f)
        for row in reader:
            batch.append(row)
            if len(batch) == batch_size:
                yield batch
                batch.clear()

        if len(batch) > 0:
            yield batch


def _gen_random_account_num_(count: int, digits: int) -> list[int]:
    unique_numbers: set[int] = set()

    lower_bound = 10 ** (digits - 1)
    upper_bound = 10**digits - 1

    while len(unique_numbers) < count:
        number = random.randint(lower_bound, upper_bound)
        unique_numbers.add(number)

    return list(unique_numbers)


async def load_accounts(file_path: str, batch_size: int, truncate: bool = False):
    await _init_db_()
    conn = Tortoise.get_connection("default")

    if truncate:
        await conn.execute_query("truncate casa_transaction cascade")
        await conn.execute_query("truncate casa_account cascade")
        await conn.execute_query("truncate casa_transfer")

    count = 0
    for batch in _read_csv_(file_path, batch_size):
        accounts = [
            AccountModel(
                account_num=row["account_num"],
                currency=row["currency"],
                balance=row["balance"],
                avail_balance=row["balance"],
                status=StatusEnum.ACTIVE,
            )
            for row in batch
        ]
        await AccountModel.bulk_create(accounts, using_db=conn)

        count += len(batch)
        print(f"Loaded {count} accounts")

    await Tortoise.close_connections()


async def _init_db_(generate_schema: bool = False):
    await Tortoise.init(
        db_url=os.environ.get("DATABASE_URL", ""),
        modules={"models": ["casa.models"]},
    )
    if generate_schema:
        await Tortoise.generate_schemas()


if __name__ == "__main__":
    args = parse_command_line_options(sys.argv[1:])
    if args.mode == "gen":
        generate_csv(args.output, int(args.count), int(args.start))
    elif args.mode == "load":
        event_loop = asyncio.new_event_loop()
        event_loop.run_until_complete(
            load_accounts(
                file_path=args.source,
                batch_size=int(args.batch),
                truncate=args.truncate,
            )
        )
        event_loop.close()
