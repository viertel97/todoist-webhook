from quarter_lib.akeyless import get_secrets
from quarter_lib.logging import setup_logging
from todoist_api_python.api import TodoistAPI

logger = setup_logging(__name__)

TODOIST_TOKEN = get_secrets(["todoist/token"])

TODOIST_API = TodoistAPI(TODOIST_TOKEN)


def add_comment_to_thread(task_id: str, comment: str):
	logger.info(f"Adding comment to task {task_id}: {comment}")
	result = TODOIST_API.add_comment(task_id=task_id, content=comment)
	return result

def add_label_to_task(task_id: str, label: str):
	logger.info(f"Adding label '{label}' to task {task_id}")
	task = TODOIST_API.get_task(task_id=task_id)
	labels = task.labels
	labels.extend(label)
	result = TODOIST_API.update_task(task_id=task_id, labels=list(set(labels)))
	return result

def get_comments_by_task_id(task_id: str):
	logger.info(f"Getting conversation for task {task_id}")
	result = TODOIST_API.get_comments(task_id=task_id)
	return result