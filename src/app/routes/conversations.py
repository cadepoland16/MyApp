from fastapi import APIRouter

from app.services.db import create_conversation, get_messages, list_conversations

router = APIRouter(prefix="/api", tags=["conversations"])


@router.get("/conversations")
def api_list_conversations():
    return {"conversations": list_conversations()}


@router.post("/conversations")
def api_create_conversation():
    cid = create_conversation()
    return {"conversation_id": cid}


@router.get("/conversations/{conversation_id}/messages")
def api_get_messages(conversation_id: str):
    return {"messages": get_messages(conversation_id)}
