from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.chat import router as chat_router

app = FastAPI(title="AI Backend")

# Health check route
app.include_router(health_router, prefix="/api")

# Chat route (OpenAI-powered)
app.include_router(chat_router, prefix="/api")