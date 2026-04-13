# CadeGPT

CadeGPT is a local-first AI chat application built with FastAPI, Jinja, vanilla JavaScript, Ollama, and Supabase. It provides a browser chat UI, persists conversations and messages in Supabase, and routes each chat request through a backend service layer instead of calling the model directly from the frontend.

The current project supports model switching inside the chat UI. A user can choose between multiple local Ollama models per message without changing the frontend code or restarting the server.

## Current Features

- FastAPI backend with a browser chat interface at `GET /chat`
- Chat API at `POST /api/chat`
- Conversation list and message history backed by Supabase
- Local Ollama inference with runtime model selection
- Structured chat responses with `model`, `env`, `timestamp`, `request_id`, and `conversation_id`
- Curated model catalog endpoint at `GET /api/models`

## Default Local Models

The app currently exposes these local chat models in the UI:

- `llama3.2:latest`
- `phi4-mini`
- `qwen2.5:7b`

The model picker is backed by a curated allowlist in the backend. You can override that list with `OLLAMA_AVAILABLE_MODELS` if you want a different set of models in the UI.

## Architecture

The project is intentionally small and straightforward:

- `src/app/main.py`: FastAPI app setup, router registration, static files
- `src/app/routes/`: HTTP routes for chat, conversations, health, and UI
- `src/app/services/chat_service.py`: chat orchestration and persistence flow
- `src/app/services/llm.py`: provider routing, model catalog, Ollama/OpenAI calls
- `src/app/services/db.py`: Supabase persistence for conversations and messages
- `src/app/templates/chat.html`: chat page template
- `src/app/static/chat.js`: frontend chat logic and model picker behavior

The request flow is:

1. The browser sends a message to `POST /api/chat`
2. The backend validates the selected model
3. The backend creates or reuses a conversation
4. The user message is stored in Supabase
5. The selected model is called through Ollama
6. The assistant reply is stored in Supabase
7. A structured response is returned to the UI

## Requirements

- Python `3.13`
- Ollama installed and running locally
- A Supabase project with `conversations` and `messages` tables
- A `.env` file in the project root

## Environment Variables

Use `.env.example` as the starting point.

Required for the current local Ollama + Supabase setup:

- `APP_ENV`
- `LLM_PROVIDER`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

Optional:

- `OLLAMA_AVAILABLE_MODELS`
- `OPENAI_API_KEY`

Notes:

- `LLM_PROVIDER=ollama` is the local model path used in this project
- `OLLAMA_MODEL` sets the default selected model
- `OLLAMA_AVAILABLE_MODELS` accepts a comma-separated list such as `llama3.2:latest,phi4-mini,qwen2.5:7b`
- `SUPABASE_SERVICE_ROLE_KEY` is required by the current database service implementation

## Run Locally

1. Create and activate a virtual environment
2. Install dependencies from `requirements.txt`
3. Copy `.env.example` to `.env` and fill in your values
4. Make sure Ollama is running locally
5. Start the FastAPI server

```bash
uvicorn app.main:app --reload --port 8000 --app-dir src
```

Then open:

```text
http://127.0.0.1:8000/chat
```

## API Endpoints

- `GET /chat`: browser UI
- `GET /api/health`: health check
- `GET /api/models`: model catalog for the chat picker
- `POST /api/chat`: send a message and receive a model response
- `GET /api/conversations`: list saved conversations
- `POST /api/conversations`: create a new conversation
- `GET /api/conversations/{conversation_id}/messages`: load messages for a conversation

Example `POST /api/chat` request:

```json
{
  "message": "Summarize the differences between FastAPI and Flask.",
  "conversation_id": null,
  "model": "qwen2.5:7b"
}
```

Example response shape:

```json
{
  "reply": "FastAPI is async-first and strongly typed...",
  "model": "qwen2.5:7b",
  "env": "dev",
  "timestamp": "2026-04-12T23:00:00.000000",
  "request_id": "uuid-here",
  "conversation_id": "uuid-here"
}
```

## Notes On Ollama Storage

Ollama stores models under:

```text
~/.ollama/models
```

Manifest files live under:

```text
~/.ollama/models/manifests
```

The actual large model files live under:

```text
~/.ollama/models/blobs
```

## Known Limitations

- The app currently uses synchronous database and HTTP calls inside FastAPI request handlers
- There is no automated test suite yet
- The current database service requires Supabase credentials at import time
- The frontend is intentionally lightweight and does not yet support streaming responses

## Future Improvements

- Per-conversation model preferences
- Streaming responses
- Better error handling around provider/database failures
- User authentication
- Conversation rename/delete support
- Test coverage for routes and service logic

Built by Cade Poland.
