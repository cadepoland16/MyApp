from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    model: str | None = None


class ChatResponse(BaseModel):
    reply: str
    model: str
    env: str
    timestamp: datetime
    request_id: str
    conversation_id: str


class ConversationSummary(BaseModel):
    id: str
    created_at: datetime


class MessageItem(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    model: str | None = None
    env: str | None = None
    request_id: str | None = None
    created_at: datetime


class ModelOption(BaseModel):
    id: str
    label: str
    description: str
    recommended: bool = False
    installed: bool | None = None


class ModelCatalogResponse(BaseModel):
    provider: str
    default_model: str
    models: list[ModelOption]
