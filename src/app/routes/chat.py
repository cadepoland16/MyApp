from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm import simple_chat

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """
    Simple chat endpoint: send a message and get an AI reply.
    """
    reply_text = simple_chat(payload.message)
    return ChatResponse(reply=reply_text)