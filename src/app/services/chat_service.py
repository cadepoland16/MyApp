from datetime import datetime
import uuid

from app.config import APP_ENV
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm import simple_chat


def handle_chat(request: ChatRequest) -> ChatResponse:
    """
    Core chat orchestration logic:
    - Takes a ChatRequest
    - Calls the LLM layer (currently mock or OpenAI)
    - Wraps the result in a structured ChatResponse with metadata
    """
    # Ask our LLM provider (mock or real, depending on APP_ENV)
    reply_text = simple_chat(request.message)

    # Decide which "model" label to report
    model_name = "mock-model" if APP_ENV == "mock" else "gpt-4o-mini"

    # Create metadata for this response
    timestamp = datetime.utcnow()
    request_id = str(uuid.uuid4())

    return ChatResponse(
        reply=reply_text,
        model=model_name,
        env=APP_ENV,
        timestamp=timestamp,
        request_id=request_id,
    )