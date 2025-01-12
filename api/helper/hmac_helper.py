import base64
import hashlib
import hmac

from quarter_lib.akeyless import get_secrets
from starlette.requests import Request

webhook_verification_token = get_secrets("todoist/webhook_verification_token")


async def verify_hmac(request: Request):
	calculated_hmac = hmac.new(webhook_verification_token.encode("utf-8"), await request.body(), hashlib.sha256).digest()
	calculated_hmac_base64 = base64.b64encode(calculated_hmac).decode()
	return request.headers.get("X-Todoist-Hmac-SHA256") == calculated_hmac_base64
