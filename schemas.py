from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: list = []

class UploadResponse(BaseModel):
    message: str
    pages: int
    chunks: int