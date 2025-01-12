from quarter_lib.akeyless import get_secrets
from quarter_lib.logging import setup_logging
from todoist_api_python.api import TodoistAPI

logger = setup_logging(__name__)

TODOIST_TOKEN = get_secrets(["todoist/token"])

TODOIST_API = TodoistAPI(TODOIST_TOKEN)


def add_comment_to_thread(task_id: str, comment: str):
    result = TODOIST_API.add_comment(task_id=task_id, content=comment)
    return result