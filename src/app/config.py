import os
from dotenv import load_dotenv

# Load values from the .env file in the project root
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "dev")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")