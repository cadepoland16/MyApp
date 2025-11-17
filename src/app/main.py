from fastapi import FastAPI
from app.routes import health

app = FastAPI(title="AI Backend")

app.include_router(health.router, prefix="/api")