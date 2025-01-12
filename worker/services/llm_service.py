import re

from quarter_lib.logging import setup_logging

from shared.services.todoist_service import add_comment_to_thread


import numpy as np
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from quarter_lib.akeyless import get_secrets

logger = setup_logging(__name__)

CHUNK_SIZE = 10
groq_api_key = get_secrets(["groq/api_key"])

chat = ChatGroq(temperature=0.5, model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

prompt = PromptTemplate(
	template="""
You are a digital assistant. Answer in the language provided.\n{message}\n""",
	input_variables=["message"],
)

chain = prompt | chat

LLM_REGEX = r"\[LLM:(.*?)\]"


def get_summary(item_list):
	# create some retry logic here
	for i in range(3):
		try:
			result = chain.invoke({"notes": item_list})["notes"]
			if len(result) != len(item_list):
				raise Exception("Result length does not match input length")
			logger.info(f"Got result from langchain: {result!s}")
			return result
		except Exception:
			logger.exception("Error in get_summary")
			raise Exception("Error in get_summary")


def get_summaries(content_list: list):
	chunks = np.array_split(list(content_list), len(list(content_list)) // CHUNK_SIZE + 1)
	summaries = []
	for chunk in chunks:
		summaries.extend(get_summary(chunk))
	return summaries

def add_llm_answer(webhook):
	if webhook.event_name == "note:added" and "[LLM:" in webhook.event_data["content"]:
		llm = re.search(LLM_REGEX, webhook.event_data["content"]).group(1)
		llm = llm.strip()
		result = chain.invoke({"message": llm})
		add_comment_to_thread(webhook.event_data["id"], result.content)

	else:
		return