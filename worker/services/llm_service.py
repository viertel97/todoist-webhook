import re

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from quarter_lib.akeyless import get_secrets
from quarter_lib.logging import setup_logging
from todoist_api_python.models import Comment
from langchain_core.messages import SystemMessage

from shared.models.webhook import Webhook
from shared.services.todoist_service import add_comment_to_thread, add_label_to_task

logger = setup_logging(__name__)

CHUNK_SIZE = 10
groq_api_key = get_secrets(["groq/api_key"])

chat = ChatGroq(temperature=0.5, model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

prompt_llm_answer = PromptTemplate(
	template="""
You are a digital assistant for comments under a task.
The content of the task is '{task_content}' including the description {description}.
Previous comments are {previous_comments}.
Answer in the language provided and keep the answers short.
\n{message}\n""",
	input_variables=["message", "task_content", "description", "previous_comments"],
)

def get_llm_answer_system_message(webhook: Webhook):
	return SystemMessage(
		content=(
			f"You are a digital assistant replying to comments under a task.\n"
			f"The content of the task is '{webhook.event_data['item']['content']}'"
			+ (f" including the description {webhook.event_data['item']['description']}"
			   				if webhook.event_data["item"]["description"] else "")
			+ "Answer in the language provided and keep the answers short.\n")
	)


prompt_categorize_task = PromptTemplate(
	template="""
You are a digital assistant. Categorize the task in the categories "Digital" and "Analogue". In general most of the tasks are digital, like preparing, writing, etc.
If the task is digital, answer "Digital". If the task is analogue, answer "Analogue".
If the task is neither, answer "None".\n{message}\n""",
	input_variables=["message"],
)

LLM_REGEX = r"@LLM:\s*(.+)"

def split_human_ai_message(comments: list[Comment]):
	previous_messages = []
	for comment in comments:
		content = comment.content.strip()
		if content.startswith("LLM:"):
			message = content[4:].strip()
			previous_messages.append(AIMessage(content=message))
		elif content.startswith("@LLM:"):
			message = content[5:].strip()
			previous_messages.append(HumanMessage(content=message))
		else:
			previous_messages.append(HumanMessage(content=content))
	return previous_messages


def add_llm_answer(webhook: Webhook, all_comments: list[Comment]):
	messages = split_human_ai_message(all_comments)
	system_message = get_llm_answer_system_message(webhook)
	full_conversation = [system_message] + messages
	result = chat(full_conversation)
	add_comment_to_thread(webhook.event_data["item"]["id"], f"LLM: {result.content}")

def categorize_task(webhook):
	message = webhook.event_data["content"]
	chain = prompt_categorize_task | chat
	result = chain.invoke({"message": message})
	result_content = result.content.replace(".","").strip()

	if result_content != "None":
		add_label_to_task(webhook.event_data["id"], result_content)
	else:
		logger.info(f"Content '{message}' could not be categorized.")