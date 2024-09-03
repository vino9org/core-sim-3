import logging

from pydantic import ValidationError
from quart import Blueprint, Response, current_app, request
from quart_schema import document_request, document_response

from . import schemas as s
from . import service

logger = logging.getLogger(__name__)

blueprint = Blueprint("casa", __name__)


@blueprint.route("/accounts/<account_num>", methods=["GET"])
@document_response(s.Account)
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
# validate request seems to have some weird behavior, so we opt for document only for now
@document_request(s.TransferRequest)
@document_response(s.Transfer, 201)
async def transfer():
    try:
        transfer_req = s.TransferRequest.model_validate(await request.json)
        result, events = await service.transfer(transfer_req)
        current_app.add_background_task(service.publish_events, events)
        logger.info(f"created transfer {result.trx_id} for amount {result.amount}")
        return result.model_dump(), 201
    except ValidationError as e:
        logger.info(f"Validation request: {str(e.errors)}")
        return {"error": "Validation Error"}, 422
    except service.InvalidRequest as e:
        logger.info(f"Invalid request: {str(e)}")
        return {"error": str(e)}, 422
    except Exception as e:
        logger.warn(f"Unexpected expection: {str(e)}")
        return {"error": str(e)}, 500
