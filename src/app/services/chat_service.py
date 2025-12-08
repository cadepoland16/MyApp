from datetime import datetime
import uuid

from app.config import APP_ENV, LLM_PROVIDER, OLLAMA_MODEL
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm import simple_chat


def handle_chat(request: ChatRequest) -> ChatResponse:
    """
    Core chat orchestration logic.

    - Takes a ChatRequest from the route layer
    - Delegates to the LLM provider (mock / ollama / openai) via simple_chat()
    - Wraps the raw reply in a structured ChatResponse with metadata
    """

    # 1️⃣ Get the raw reply text from our LLM layer
    reply_text = simple_chat(request.message)

    # 2️⃣ Decide which "model" label to report based on env + provider
    provider = (LLM_PROVIDER or "mock").lower()

    if APP_ENV == "mock" or provider == "mock":
        model_name = "mock-model"
    elif provider == "ollama":
        # Example: "ollama:llama3.2:latest"
        model_name = f"ollama:{OLLAMA_MODEL}"
    elif provider == "openai":
        model_name = "gpt-4o-mini"
    else:
        model_name = f"unknown-provider:{provider}"

    # 3️⃣ Create metadata
    timestamp = datetime.utcnow()
    request_id = str(uuid.uuid4())

    # 4️⃣ Return a structured response
    return ChatResponse(
        reply=reply_text,
        model=model_name,
        env=APP_ENV,
        timestamp=timestamp,
        request_id=request_id,
    )