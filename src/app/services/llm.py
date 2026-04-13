from typing import Optional, Tuple
import requests
from openai import OpenAI

from app.config import (
    APP_ENV,
    OPENAI_API_KEY,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_AVAILABLE_MODELS,
    OLLAMA_MODEL,
)

_openai_client: Optional[OpenAI] = None
_DEFAULT_OLLAMA_MODELS = [
    {
        "id": "llama3.2:latest",
        "label": "Llama 3.2",
        "description": "Fast default for everyday chat.",
        "recommended": True,
    },
    {
        "id": "phi4-mini",
        "label": "Phi-4 Mini",
        "description": "Compact reasoning-focused option.",
        "recommended": True,
    },
    {
        "id": "qwen2.5:7b",
        "label": "Qwen 2.5 7B",
        "description": "Stronger structured output and coding.",
        "recommended": True,
    },
]


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set in the environment.")
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def _humanize_model_name(model_id: str) -> str:
    name = model_id.replace(":latest", "")
    return name.replace("-", " ").title()


def _get_installed_ollama_models() -> set[str] | None:
    try:
        response = requests.get(f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags", timeout=3)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    installed = set()
    for item in data.get("models", []):
        name = (item.get("name") or "").strip()
        if not name:
            continue
        installed.add(name)
        installed.add(name.split(":", 1)[0])
    return installed


def _configured_ollama_models() -> list[dict[str, object]]:
    if not OLLAMA_AVAILABLE_MODELS:
        configured = [dict(model) for model in _DEFAULT_OLLAMA_MODELS]
    else:
        configured = []
        for raw_model in OLLAMA_AVAILABLE_MODELS.split(","):
            model_id = raw_model.strip()
            if not model_id:
                continue
            configured.append(
                {
                    "id": model_id,
                    "label": _humanize_model_name(model_id),
                    "description": "Configured in OLLAMA_AVAILABLE_MODELS.",
                    "recommended": model_id == OLLAMA_MODEL,
                }
            )

    ids = {str(model["id"]) for model in configured}
    if OLLAMA_MODEL not in ids:
        configured.insert(
            0,
            {
                "id": OLLAMA_MODEL,
                "label": _humanize_model_name(OLLAMA_MODEL),
                "description": "Current default model from OLLAMA_MODEL.",
                "recommended": True,
            },
        )

    return configured


def get_model_catalog() -> dict[str, object]:
    if LLM_PROVIDER != "ollama":
        return {
            "provider": LLM_PROVIDER,
            "default_model": OLLAMA_MODEL,
            "models": [],
        }

    installed = _get_installed_ollama_models()
    models = []
    for model in _configured_ollama_models():
        model_id = str(model["id"])
        models.append(
            {
                **model,
                "installed": None if installed is None else model_id in installed,
            }
        )

    return {
        "provider": LLM_PROVIDER,
        "default_model": OLLAMA_MODEL,
        "models": models,
    }


def resolve_chat_model(requested_model: str | None) -> str:
    if LLM_PROVIDER == "mock" or APP_ENV == "mock":
        return requested_model or "mock"

    if LLM_PROVIDER != "ollama":
        return requested_model or "gpt-4o-mini"

    catalog = get_model_catalog()
    allowed_models = {str(model["id"]) for model in catalog["models"]}
    chosen_model = (requested_model or OLLAMA_MODEL).strip()

    if chosen_model not in allowed_models:
        raise ValueError(f"Model '{chosen_model}' is not enabled for this app.")

    installed_entry = next(
        (model for model in catalog["models"] if model["id"] == chosen_model),
        None,
    )
    if installed_entry and installed_entry.get("installed") is False:
        raise ValueError(
            f"Model '{chosen_model}' is allowed but not installed in Ollama."
        )

    return chosen_model


def simple_chat(message: str, model: str | None = None) -> Tuple[str, str]:
    provider = (LLM_PROVIDER or "mock").lower()

    if provider == "mock" or APP_ENV == "mock":
        model_name = model or "mock"
        return (f"[MOCK REPLY:{model_name}] You said: {message}", model_name)

    if provider == "ollama":
        chosen_model = resolve_chat_model(model)
        text = _ollama_chat(message, chosen_model)
        return (text, chosen_model)

    if provider == "openai":
        text = _openai_chat(message)
        return (text, "gpt-4o-mini")

    raise RuntimeError(f"Unknown LLM_PROVIDER: {provider}")


def _ollama_chat(message: str, model: str) -> str:
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "stream": False,
        "messages": [{"role": "user", "content": message}],
    }

    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()

    msg = data.get("message") or {}
    content = msg.get("content")
    if not content:
        raise RuntimeError(f"Ollama response missing message.content: {data}")

    return content


def _openai_chat(message: str) -> str:
    client = _get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful, concise assistant."},
            {"role": "user", "content": message},
        ],
    )
    return response.choices[0].message.content or ""
