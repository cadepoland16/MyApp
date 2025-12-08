from typing import Optional

import requests
from openai import OpenAI

from app.config import (
    APP_ENV,
    OPENAI_API_KEY,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)


# We'll create the OpenAI client lazily so it doesn't matter
# if you don't have a key when using mock or ollama.
_openai_client: Optional[OpenAI] = None


def _get_openai_client() -> OpenAI:
    global _openai_client

    if _openai_client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)

    return _openai_client


def simple_chat(message: str) -> str:
    """
    Core LLM dispatch function.

    - If LLM_PROVIDER == 'mock' OR APP_ENV == 'mock' -> return a mock reply
    - If LLM_PROVIDER == 'ollama'                    -> call local Ollama
    - If LLM_PROVIDER == 'openai'                    -> call OpenAI (future paid mode)
    """

    provider = (LLM_PROVIDER or "mock").lower()

    # Always respect mock environment first
    if provider == "mock" or APP_ENV == "mock":
        return f"[MOCK REPLY] You said: {message}"

    if provider == "ollama":
        return _ollama_chat(message)

    if provider == "openai":
        return _openai_chat(message)

    raise RuntimeError(f"Unknown LLM_PROVIDER: {provider}")


def _ollama_chat(message: str) -> str:
    """
    Call a local Ollama model via its HTTP /api/chat endpoint.
    Docs: http://localhost:11434/api/chat (when Ollama is running)
    """
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"

    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,  # get a single JSON response instead of a stream
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ],
    }

    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()

    # According to the docs, the assistant reply is in data["message"]["content"]
    # example response: {"model": "...", "message": {"role": "assistant", "content": "..."}}
    message_obj = data.get("message") or {}
    content = message_obj.get("content")

    if not content:
        raise RuntimeError(f"Ollama response missing message.content: {data}")

    return content


def _openai_chat(message: str) -> str:
    """
    Call OpenAI's chat completions API (when you choose to pay for it later).
    """
    client = _get_openai_client()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful, concise assistant."},
            {"role": "user", "content": message},
        ],
    )

    return response.choices[0].message.content or ""