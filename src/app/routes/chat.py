from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse, ModelCatalogResponse
from app.services.chat_service import handle_chat
from app.services.llm import get_model_catalog

router = APIRouter()


@router.get("/models", response_model=ModelCatalogResponse)
async def models_endpoint():
    return get_model_catalog()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    try:
        return handle_chat(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
