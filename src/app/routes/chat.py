from datetime import datetime
import uuid

from fastapi import APIRouter

from app.config import APP_ENV
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm import simple_chat

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """
    Simple chat endpoint: send a message and get an AI (or mock) reply.
    Returns a structured response with metadata useful for logging, UI, etc.
    """
    # Ask our LLM service (currently mock in APP_ENV=mock)
    reply_text = simple_chat(payload.message)

    # Decide which "model" label to report
    model_name = "mock-model" if APP_ENV == "mock" else "gpt-4o-mini"

    # Create a unique request id and timestamp
    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()

    return ChatResponse(
        reply=reply_text,
        model=model_name,
        env=APP_ENV,
        timestamp=timestamp,
        request_id=request_id,
    )