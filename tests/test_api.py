from fastapi.testclient import TestClient


def _force_ollama_mode(monkeypatch, llm_module):
    monkeypatch.setattr(llm_module, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(llm_module, "OLLAMA_MODEL", "llama3.2:latest")


def test_health_endpoint():
    from app.main import app

    client = TestClient(app)
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_models_endpoint_returns_curated_catalog(monkeypatch):
    from app.main import app
    from app.services import llm

    _force_ollama_mode(monkeypatch, llm)
    monkeypatch.setattr(
        llm, "_get_installed_ollama_models", lambda: {"llama3.2:latest", "phi4-mini", "qwen2.5:7b"}
    )

    client = TestClient(app)
    response = client.get("/api/models")

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "ollama"
    assert data["default_model"] == "llama3.2:latest"
    assert [model["id"] for model in data["models"]] == [
        "llama3.2:latest",
        "phi4-mini",
        "qwen2.5:7b",
    ]
    assert all(model["installed"] is True for model in data["models"])


def test_chat_endpoint_rejects_disabled_model(monkeypatch):
    from app.main import app
    from app.services import llm

    _force_ollama_mode(monkeypatch, llm)

    client = TestClient(app)
    response = client.post("/api/chat", json={"message": "hello", "model": "gemma3:4b"})

    assert response.status_code == 400
    assert "not enabled" in response.json()["detail"]


def test_chat_endpoint_uses_selected_model(monkeypatch):
    from app.main import app
    from app.services import chat_service, llm

    writes = []

    _force_ollama_mode(monkeypatch, llm)
    monkeypatch.setattr(
        llm, "_get_installed_ollama_models", lambda: {"llama3.2:latest", "phi4-mini", "qwen2.5:7b"}
    )
    monkeypatch.setattr(chat_service, "create_conversation", lambda: "conversation-123")
    monkeypatch.setattr(
        chat_service,
        "simple_chat",
        lambda message, model=None: (f"reply:{message}", model or "llama3.2:latest"),
    )
    monkeypatch.setattr(chat_service, "add_message", lambda **kwargs: writes.append(kwargs))

    client = TestClient(app)
    response = client.post("/api/chat", json={"message": "hello", "model": "phi4-mini"})

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "reply:hello"
    assert data["model"] == "phi4-mini"
    assert data["conversation_id"] == "conversation-123"
    assert writes[0]["model"] == "phi4-mini"
    assert writes[1]["model"] == "phi4-mini"


def test_chat_page_renders_model_picker(monkeypatch):
    from app.main import app
    from app.services import llm

    _force_ollama_mode(monkeypatch, llm)
    monkeypatch.setattr(
        llm, "_get_installed_ollama_models", lambda: {"llama3.2:latest", "phi4-mini", "qwen2.5:7b"}
    )

    client = TestClient(app)
    response = client.get("/chat")

    assert response.status_code == 200
    assert 'id="modelSelect"' in response.text
    assert "Phi-4 Mini" in response.text
    assert "/static/chat.js?v=2026-04-12-2" in response.text
