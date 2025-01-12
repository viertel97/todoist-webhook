from json import JSONDecodeError, loads
from platform import platform

from fastapi import Request
from loguru import logger


DEBUG = platform == "darwin" or platform == "win32" or platform == "Windows"


async def log_request_info(request: Request):
    logger.debug(f"{request.method} {request.url}")
    if request.path_params.items():
        logger.debug("Params:")
        for name, value in request.path_params.items():
            logger.debug(f"\t{name}: {value}")
    if request.headers.items():
        logger.debug("Headers:")
        for name, value in request.headers.items():
            logger.debug(f"\t{name}: {value}")
    logger.debug("Body:")
    try:
        request_body = await request.json()
        try:
            request_body = loads(request_body)
        except Exception:
            pass
        if isinstance(request_body, list):
            for item in request_body:
                for key in item.keys():
                    logger.debug(f"\t{key}: {item[key]}")
        else:
            for key in request_body.keys():
                logger.debug(f"\t{key}: {request_body[key]}")
    except JSONDecodeError:
        logger.debug("Wrong Empty body")
    except UnicodeDecodeError:
        logger.debug("Wrong Empty body")

def get_url(service):
    if DEBUG:
        return "http://192.168.178.49:9300"
    else:
        return f"http://{service}.custom.svc.cluster.local:80"
