import os
import traceback
from pathlib import Path
from sys import platform

import uvicorn
from celery import Celery
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from quarter_lib.logging import setup_logging

from api.config.api_documentation import description, tags_metadata, title
from api.helper.network_helper import log_request_info, DEBUG
from api.proxy.telegram_proxy import log_to_telegram
from api.router.main_router import router as main_controller_router
from shared.config.constants import REDIS_URL

routers = [main_controller_router]
logger = setup_logging(__name__)

IS_CONTAINER = os.environ.get("IS_CONTAINER", "False") == "True"
logger.info(
    "Variables:\nDEBUG: {}\nIS_CONTAINER: {}\nplatform: {}".format(
        DEBUG, IS_CONTAINER, platform
    )
)
app = FastAPI(openapi_tags=tags_metadata, title=title, description=description)

[
    app.include_router(router, dependencies=[Depends(log_request_info)])
    for router in routers
]


celery_app = Celery(
    __name__,
    broker=REDIS_URL,
    backend=REDIS_URL,
)


@app.get("/")
def health():
    return {"status": "ok"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.info(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    items = request.path_params.items()
    headers = request.headers.items()

    request_logging_string = (
        f"{request.method} {request.url}\n\n Headers:\n{headers}\n\nItems:\n{items}"
    )
    exception_logging_string = f"{exc.__class__.__name__}: {exc}\n\n{''.join(traceback.TracebackException.from_exception(exc).format())}"
    logging_string = f"Exception:\n{exception_logging_string}\n---------\nRequest:\n{request_logging_string}\n\n"
    # await log_to_telegram(logging_string, logger)
    logger.error(logging_string)
    return JSONResponse(
        content={
            "status_code": 500,
            "message": "Internal Server Error",
            "data": None,
        },
        status_code=500,
    )


if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app", host="0.0.0.0", port=9400, workers=1)
