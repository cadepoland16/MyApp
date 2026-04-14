# Contributing

## Scope

This project is a small FastAPI-based AI application. Contributions should keep the codebase simple, readable, and easy to run locally.

## Local Setup

1. Create a Python `3.13` virtual environment
2. Install runtime dependencies with `pip install -r requirements.txt`
3. Install test dependencies with `pip install -r requirements-dev.txt`
4. Copy `.env.example` to `.env`
5. Fill in Supabase credentials and local Ollama settings

## Running The App

```bash
uvicorn app.main:app --reload --port 8000 --app-dir src
```

## Running Tests

```bash
pytest
```

## Linting And Formatting

```bash
ruff check src tests
ruff format --check src tests
```

## Contribution Guidelines

- Keep changes scoped and focused
- Prefer small, reviewable commits
- Update documentation when behavior changes
- Add or update tests for API and service behavior when practical
- Keep `ruff check`, `ruff format --check`, and `pytest` passing before opening a PR
- Avoid committing secrets, local credentials, or generated files

## Pull Request Expectations

- Describe the problem being solved
- Summarize the behavior change
- Include verification steps
- Call out any tradeoffs or known limitations
