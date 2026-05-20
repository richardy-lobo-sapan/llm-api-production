import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"Key: {key[:20]}...")

supabase = create_client(url, key)

try:
    result = supabase.table("chat_history").select("*").limit(1).execute()
    print(f"Connection OK! Data: {result.data}")
except Exception as e:
    print(f"Error: {e}")