import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def save_message(session_id: str, role: str, content: str):
    try:
        result = supabase.table("chat_history").insert({
            "session_id": session_id,
            "role": role,
            "content": content
        }).execute()
        print(f"DB insert result: {result}")
    except Exception as e:
        print(f"DB error: {e}")

def get_history(session_id: str):
    try:
        result = supabase.table("chat_history").select("*").eq(
            "session_id", session_id
        ).order("created_at").execute()
        return result.data
    except Exception as e:
        print(f"DB error: {e}")
        return []

def get_all_sessions():
    try:
        result = supabase.table("chat_history").select(
            "session_id"
        ).execute()
        sessions = list(set([r["session_id"] for r in result.data]))
        return sessions
    except Exception as e:
        print(f"DB error: {e}")
        return []