from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from quarter_lib.logging import setup_logging
from starlette.requests import Request

from shared.models.webhook import Webhook
from main_worker import process_webhook
from quarter_lib.akeyless import get_secrets
import hmac
import hashlib

logger = setup_logging(__name__)
router = APIRouter()

verification_token, webhook_client_secret = get_secrets(["todoist/webhook_verification_token", "todoist/webhook_client_secret"])


@router.post("/")
async def persist_webhook(request: Request, webhook: Webhook):
    hmac_to_check = request.headers["X-Todoist-Hmac-SHA256"]
    signature = hmac.new(
        key=webhook_client_secret,
        msg=str(webhook.dict()),
        digestmod=hashlib.sha256
    ).hexdigest().upper()
    logger.info(f"Received Todoist webhook: {webhook.event_name}")
    result = process_webhook.delay(jsonable_encoder(webhook))
    result_output = result.get()
    logger.info(result_output)
    return {"status": "ok"}
