from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.chat import router as chat_router
from app.routes.conversations import router as conversations_router
from app.routes.health import router as health_router
from app.routes.ui import router as ui_router

app = FastAPI(title="CadeGPT")

app.include_router(conversations_router)

BASE_DIR = Path(__file__).resolve().parent  # src/app

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(ui_router)

app.include_router(health_router, prefix="/api")

app.include_router(chat_router, prefix="/api")
