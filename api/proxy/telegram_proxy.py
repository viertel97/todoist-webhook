from threading import Thread

from requests import post

from api.config.api_documentation import title
from api.helper.network_helper import get_url

URL = get_url("telegram-service")


async def send_file_to_telegram(caption: str, file):
    post(URL + "/file", json={"caption": caption}, files=file)
    return {"message": "File sent to telegram"}


async def send_message_to_telegram(message: str):
    post(URL + "/message", json={"message": message})
    return {"message": "Message sent to telegram"}


async def log_to_telegram(message: str, logger):
    logger.info(f"service: {title}, message: {message}")
    Thread(
        target=post,
        args=(URL + "/log",),
        kwargs={"json": {"service": title, "message": message}},
    ).start()
    return {"message": "Message sent to telegram"}
