from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import handle_chat

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """
    HTTP endpoint that delegates to the chat service.
    Keeps the route thin and reusable for other interfaces.
    """
    return handle_chat(payload)