from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from quarter_lib.logging import setup_logging

from shared.models.webhook import Webhook
from worker.main import process_webhook

logger = setup_logging(__name__)
router = APIRouter()


@router.post("/")
async def persist_webhook(webhook: Webhook):
    logger.info(f"Received Todoist webhook: {webhook.event_name}")
    result = process_webhook.delay(jsonable_encoder(webhook))
    result_output = result.get()
    logger.info(result_output)
    return {"status": "ok"}
