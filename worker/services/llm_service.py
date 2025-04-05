import re

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from quarter_lib.akeyless import get_secrets
from quarter_lib.logging import setup_logging

from shared.services.todoist_service import add_comment_to_thread, add_label_to_task

logger = setup_logging(__name__)

CHUNK_SIZE = 10
groq_api_key = get_secrets(["groq/api_key"])

chat = ChatGroq(temperature=0.5, model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

prompt_llm_answer = PromptTemplate(
	template="""
You are a digital assistant. Answer in the language provided and keep the answers short.\n{message}\n""",
	input_variables=["message"],
)

prompt_categorize_task = PromptTemplate(
	template="""
You are a digital assistant. Categorize the task in the categories "Digital" and "Analogue". In general most of the tasks are digital, like preparing, writing, etc.
If the task is digital, answer "Digital". If the task is analogue, answer "Analogue".
If the task is neither, answer "None".\n{message}\n""",
	input_variables=["message"],
)

LLM_REGEX = r"@LLM:\s*(.+)"


def add_llm_answer(webhook):
	message = re.search(LLM_REGEX, webhook.event_data["content"]).group(1)
	message = message.strip()
	chain = prompt_llm_answer | chat
	result: AIMessage = chain.invoke({"message": message})
	add_comment_to_thread(webhook.event_data["item"]["id"], f"LLM: {result.content}")

def categorize_task(webhook):
	message = webhook.event_data["content"]
	chain = prompt_categorize_task | chat
	result: AIMessage = chain.invoke({"message": message})
	result_content = result.content.replace(".","").strip()
	if result_content != "None":
		add_label_to_task(webhook.event_data["id"], result_content)
	else:
		logger.info(f"Content '{message}' could not be categorized.")