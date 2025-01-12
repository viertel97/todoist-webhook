import re

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from quarter_lib.akeyless import get_secrets
from quarter_lib.logging import setup_logging

from shared.services.todoist_service import add_comment_to_thread

logger = setup_logging(__name__)

CHUNK_SIZE = 10
groq_api_key = get_secrets(["groq/api_key"])

chat = ChatGroq(temperature=0.5, model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

prompt = PromptTemplate(
	template="""
You are a digital assistant. Answer in the language provided and keep the answers short.\n{message}\n""",
	input_variables=["message"],
)

chain = prompt | chat

LLM_REGEX = r"@LLM:\s*(.+)"


def add_llm_answer(webhook):
	message = re.search(LLM_REGEX, webhook.event_data["content"]).group(1)
	message = message.strip()
	result: AIMessage = chain.invoke({"message": message})
	add_comment_to_thread(webhook.event_data["item"]["id"], f"LLM: {result.content}")
