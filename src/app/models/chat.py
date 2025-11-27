from datetime import datetime
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """
    Incoming payload from the client.
    """
    message: str


class ChatResponse(BaseModel):
    """
    Outgoing response from the API for a single chat turn.
    """
    reply: str                 # what the assistant says
    model: str                 # which model/provider generated it (or mock)
    env: str                   # current environment, e.g. "mock", "dev", "prod"
    timestamp: datetime        # when the response was generated (UTC)
    request_id: str            # unique id for this request/response