from datetime import UTC, datetime
import uuid

from app.config import APP_ENV
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm import resolve_chat_model, simple_chat
from app.services.db import create_conversation, add_message


def handle_chat(request: ChatRequest) -> ChatResponse:
    selected_model = getattr(request, "model", None)
    selected_model = resolve_chat_model(selected_model)
    conversation_id = getattr(request, "conversation_id", None) or create_conversation()

    request_id = str(uuid.uuid4())
    timestamp = datetime.now(UTC)

    add_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
        model=selected_model,
        env=APP_ENV,
        request_id=request_id,
    )

    reply_text, model_used = simple_chat(request.message, model=selected_model)

    add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=reply_text,
        model=model_used,
        env=APP_ENV,
        request_id=request_id,
    )

    return ChatResponse(
        reply=reply_text,
        model=model_used,
        env=APP_ENV,
        timestamp=timestamp,
        request_id=request_id,
        conversation_id=conversation_id,
    )
