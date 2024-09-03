import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException
from tortoise.contrib.pydantic import PydanticModel

from . import schemas as s
from . import service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/casa")


@router.get("/accounts/{account_num}", response_model=s.Account)
async def get_account_details(account_num: str) -> PydanticModel:
    account = await service.get_account_details(account_num)
    if account:
        return account

    raise HTTPException(status_code=404, detail="Account not found or inactive")


@router.post("/transfers", response_model=s.Transfer, status_code=201)
async def transfer(
    transfer_req: s.TransferRequest,
    background_tasks: BackgroundTasks,
) -> PydanticModel:
    try:
        transfer, transactions = await service.transfer(transfer_req)
        background_tasks.add_task(service.publish_events, transactions)
        logger.info(f"processed request: {transfer_req.ref_id}")
        return transfer
    except service.InvalidRequest as e:
        logger.info(f"request is invalid: {transfer_req.ref_id}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception(f"An error occured: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
