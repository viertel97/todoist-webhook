from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from quarter_lib.logging import setup_logging
from starlette.requests import Request

from api.helper.hmac_helper import verify_hmac
from shared.models.webhook import Webhook
from main_worker import process_webhook
from quarter_lib.akeyless import get_secrets
import hmac
import hashlib

logger = setup_logging(__name__)
router = APIRouter()


@router.post("/")
async def persist_webhook(request: Request, webhook: Webhook):
    is_valid = await verify_hmac(request)
    if not is_valid:
        return {"status": "invalid hmac"}
    logger.info(f"Received Todoist webhook: {webhook.event_name}")
    result = process_webhook.delay(jsonable_encoder(webhook))
    result_output = result.get()
    logger.info(result_output)
    return {"status": "ok"}
