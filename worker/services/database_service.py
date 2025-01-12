import math

import pandas as pd
from quarter_lib.logging import setup_logging

from shared.models.webhook import Webhook
from worker.helper.database_helper import create_sqlalchemy_engine

logger = setup_logging(__name__)

ENGINE = create_sqlalchemy_engine()


def insert_webhook_into_database(webhook: Webhook):
    df = pd.json_normalize([webhook.model_dump()], sep="~")
    for column in ["event_data~labels", "event_data~item~labels"]:
        if column in df.columns:
            df[column] = df[column].apply(
                lambda x: str(x) if isinstance(x, list) and len(x) > 0 else math.nan
            )
    result = df.to_sql("todoist_webhooks", con=ENGINE, if_exists="append", index=False)
    logger.info(f"Inserted {result} webhook(s) into database")
    return result
