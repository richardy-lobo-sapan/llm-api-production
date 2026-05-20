import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from schemas import ChatRequest, ChatResponse, UploadResponse
from database import save_message, get_history, get_all_sessions
from rag import process_pdf, answer_question

load_dotenv()

app = FastAPI(
    title="LLM API Production",
    description="Production-ready LLM API with RAG, Langfuse observability, and Supabase storage",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        pages, chunks = process_pdf(tmp_path)
        return UploadResponse(
            message=f"Successfully processed {file.filename}",
            pages=pages,
            chunks=chunks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        save_message(request.session_id, "user", request.message)
        answer, sources = answer_question(request.message, request.session_id)
        save_message(request.session_id, "assistant", answer)

        return ChatResponse(
            answer=answer,
            session_id=request.session_id,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
def get_chat_history(session_id: str):
    history = get_history(session_id)
    return {"session_id": session_id, "history": history}

@app.get("/sessions")
def list_sessions():
    sessions = get_all_sessions()
    return {"sessions": sessions}