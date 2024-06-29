import logging

from pydantic import ValidationError
from quart import Blueprint, Response, current_app, request

from . import schemas as s
from . import service

logger = logging.getLogger(__name__)

blueprint = Blueprint("casa", __name__)


@blueprint.route("/accounts/<account_num>", methods=["GET"])
async def get_account_details(
    account_num: str,
):
    try:
        account = await service.get_account_details(account_num)
        if account:
            return account.model_dump()
        else:
            return {"error": "Account not found or not active"}, 404
    except Exception as e:
        logger.warn(f"Unexpected expection: {str(e)}")
        return Response({"error": str(e)}, status=500)


@blueprint.route("/transfers", methods=["POST"])
async def transfer():
    try:
        transfer_req = s.TransferRequest.model_validate(await request.json)
        result, events = await service.transfer(transfer_req)
        current_app.add_background_task(service.publish_events, events)
        logger.info(f"created transfer {result.trx_id} for amount {result.amount}")
        return result.model_dump(), 201
    except (service.InvalidRequest, ValidationError) as e:
        logger.info(f"Invalid request: {str(e)}")
        return Response({"error": str(e)}, status=422)
    except Exception as e:
        logger.warn(f"Unexpected expection: {str(e)}")
        return Response({"error": str(e)}, status=500)
