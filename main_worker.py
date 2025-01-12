import re
from datetime import datetime

from celery import Celery, current_task
from quarter_lib.logging import setup_logging

from shared.config.constants import REDIS_URL
from shared.models.webhook import Webhook
from worker.services.database_service import insert_webhook_into_database
from worker.services.llm_service import add_llm_answer

logger = setup_logging(__name__)

app = Celery(
    __name__,
    broker=REDIS_URL,
    backend=REDIS_URL,
)
app.conf.task_routes = {"app.worker.celery_worker.queue": "items"}
app.conf.update(task_track_started=True)



@app.task(name="app.worker.celery_worker.queue")
def process_webhook(webhook_json: dict) -> str:
    logger.info(f"Processing webhook: {webhook_json}")
    webhook = Webhook.model_validate(webhook_json)

    logger.info(
        f"Task started at {datetime.now()} - Task ID: {current_task.request.id}"
    )
    result = insert_webhook_into_database(webhook)

    # add_llm_answer(webhook)

    return f"Task completed at {datetime.now()} with result: {result}"


if __name__ == "__main__":
    worker = app.Worker(
        app=app, concurrency=1, loglevel="INFO", hostname="worker1", queues=["items"]
    )
    worker.start()
