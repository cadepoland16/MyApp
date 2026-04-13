from pathlib import Path
import traceback

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.llm import get_model_catalog

router = APIRouter()

APP_DIR = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = APP_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    try:
        from app import config

        supabase_url = getattr(config, "SUPABASE_URL", "") or ""
        supabase_anon_key = getattr(config, "SUPABASE_ANON_KEY", "") or ""
        model_catalog = get_model_catalog()

        return templates.TemplateResponse(
            request,
            "chat.html",
            {
                "supabase_url": supabase_url,
                "supabase_anon_key": supabase_anon_key,
                "model_catalog": model_catalog,
                "asset_version": "2026-04-12-2",
            },
        )
    except Exception:
        tb = traceback.format_exc()
        return HTMLResponse(
            content=f"""
            <h2>/chat crashed (500)</h2>
            <p><b>templates dir:</b> {TEMPLATES_DIR}</p>
            <pre style="white-space:pre-wrap">{tb}</pre>
            """,
            status_code=500,
        )
