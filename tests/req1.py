import argparse
import json
import sys
from datetime import datetime
from urllib import request
from urllib.error import HTTPError
from uuid import uuid4

#
# test script to send rquest to API server.
# can run with standard python3 without external dependencies
#
#


def payload(
    from_account,
    to_account,
    amount,
):
    ref_id = uuid4().hex
    return {
        "ref_id": ref_id,
        "trx_date": datetime.now().strftime("%Y-%m-%d"),
        "debit_account_num": from_account,
        "credit_account_num": to_account,
        "currency": "USD",
        "amount": float(amount),
        "memo": f"test trasnfer {ref_id}",
    }


def get_account(url, account_num):
    with request.urlopen(f"{url}/{account_num}") as response:
        print(response.status)
        print(json.dumps(json.loads(response.read()), indent=4))


def transfer_request(url, payload):
    req = request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req) as response:
            print(response.status)
            print(json.dumps(json.loads(response.read()), indent=4))
    except HTTPError as e:
        print(f"http_status={e.code},{e.read().decode()}")


def parse_commandline_options(args):
    parser = argparse.ArgumentParser(description="Send request to API")
    parser.add_argument(
        "-H",
        "--host",
        dest="host",
        default="http://localhost:5000/api/casa",
    )
    parser.add_argument(
        "--api",
        dest="api",
        default="transfer",
        help="transfer or account",
    )
    parser.add_argument(
        "source",
        nargs="?",
        default="A408944657",
        help="debit account",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="A754974758",
        help="credit account",
    )
    parser.add_argument(
        "amount",
        nargs="?",
        default="100.00",
        help="debit account",
    )

    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_commandline_options(sys.argv[1:])
    # print(args)
    if args.api == "transfer":
        transfer_request(
            f"{args.host}/transfers",
            payload(args.source, args.target, args.amount),
        )
    elif args.api == "account":
        get_account(f"{args.host}/accounts", args.source)
    else:
        print(f"unknown api: {args.api}")
