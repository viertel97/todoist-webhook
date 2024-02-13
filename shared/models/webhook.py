
from pydantic import BaseModel


class Webhook(BaseModel):
    event_data: dict
    event_name: str
    initiator: dict
    user_id: str
    version: str
