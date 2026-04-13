import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
_sb: Client | None = None


def _get_client() -> Client:
    global _sb
    if _sb is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError("Missing SUPABASE_URL and/or SUPABASE_SERVICE_ROLE_KEY in .env")
        _sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _sb

def list_conversations(limit: int = 50):
    resp = (
        _get_client().table("conversations")
        .select("id,created_at")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data or []

def create_conversation() -> str:
    resp = _get_client().table("conversations").insert({}).execute()
    data = resp.data or []
    return data[0]["id"]

def get_messages(conversation_id: str, limit: int = 200):
    resp = (
        _get_client().table("messages")
        .select("id,conversation_id,role,content,created_at,model,env,request_id")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return resp.data or []

def add_message(
    conversation_id: str,
    role: str,
    content: str,
    model: str | None = None,
    env: str | None = None,
    request_id: str | None = None,
):
    _get_client().table("messages").insert(
        {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "model": model,
            "env": env,
            "request_id": request_id,
        }
    ).execute()
