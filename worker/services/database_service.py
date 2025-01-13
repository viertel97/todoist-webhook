import json

import pymysql
from quarter_lib.logging import setup_logging

from shared.models.webhook import Webhook
from worker.helper.database_helper import create_server_connection

logger = setup_logging(__name__)


def insert_webhook_into_database(webhook: Webhook) -> None:
	json_data = json.dumps(webhook.model_dump(), indent=4)
	connection = create_server_connection()
	with connection.cursor() as cursor:
		try:
			cursor.execute(
				"INSERT INTO todoist_webhooks_v2 (data) VALUES (%s)",
				(json_data,)
			)
			connection.commit()
		except pymysql.err.IntegrityError as e:
			logger.error(f"IntegrityError: {e}")
			connection.rollback()
			raise e
	close_server_connection(connection)