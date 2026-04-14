from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

APP_ENV = os.getenv("APP_ENV", "dev")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_AVAILABLE_MODELS = os.getenv("OLLAMA_AVAILABLE_MODELS", "").strip()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

if APP_ENV != "prod":
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("Supabase config missing. Loaded .env from:", ENV_PATH)
    else:
        print("Supabase config loaded from:", ENV_PATH)
