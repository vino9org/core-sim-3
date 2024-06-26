import logging

from pydantic import ValidationError
from quart import Blueprint, Response, request

from . import schemas, service

logger = logging.getLogger(__name__)

blueprint = Blueprint("casa", __name__)


@blueprint.route("/accounts/<account_num>", methods=["GET"])
async def get_account_details(
    account_num: str,
):
    account = await service.get_account_details(account_num)
    if account:
        return account.dict()
    else:
        return Response(status=404)


@blueprint.route("/transfers", methods=["POST"])
async def transfer():
    try:
        transfer_req = schemas.TransferSchema.parse_obj(await request.json)
        result = await service.transfer(transfer_req)
        return result.dict(), 201
    except (service.InvalidRequest, ValidationError) as e:
        logger.info(f"Invalid request: {str(e)}")
        return Response({"error": str(e)}, status=422)
