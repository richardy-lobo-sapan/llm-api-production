# LLM API Production

A production-ready LLM API with **FastAPI**, **RAG (Retrieval-Augmented Generation)**, **Langfuse observability**, and **Supabase** persistent storage — deployed on Railway.

![Python](https://img.shields.io/badge/python-3.12-blue) ![Railway](https://img.shields.io/badge/deployed-Railway-purple) ![License](https://img.shields.io/badge/license-MIT-green)

🚀 **Live API:** https://llm-api-production-production.up.railway.app/docs

---

## What It Does

Upload any PDF document and ask questions about it. Every conversation is saved to a database, and every LLM call is traced for observability.

```
User uploads PDF
        ↓
API extracts text → splits into chunks → embeds with Gemini
        ↓
User asks a question
        ↓
API retrieves relevant chunks → sends to Gemini → returns answer
        ↓
Conversation saved to Supabase → trace logged to Langfuse
```

---

## Demo

[![UI Swagger](https://github.com/richardy-lobo-sapan/llm-api-production/raw/main/docs/4_uiswagger.png)](/richardy-lobo-sapan/llm-api-production/blob/main/docs/4_uiswagger.png)

[![Document](https://github.com/richardy-lobo-sapan/llm-api-production/raw/main/docs/4_document.png)](/richardy-lobo-sapan/llm-api-production/blob/main/docs/4_document.png)

[![Chat](https://github.com/richardy-lobo-sapan/llm-api-production/raw/main/docs/4_chat.png)](/richardy-lobo-sapan/llm-api-production/blob/main/docs/4_chat.png)

[![History](https://github.com/richardy-lobo-sapan/llm-api-production/raw/main/docs/4_history.png)](/richardy-lobo-sapan/llm-api-production/blob/main/docs/4_history.png)

[![LangFuse](https://github.com/richardy-lobo-sapan/llm-api-production/raw/main/docs/4_langfuse.png)](/richardy-lobo-sapan/llm-api-production/blob/main/docs/4_langfuse.png)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/upload` | Upload and process a PDF |
| POST | `/chat` | Ask a question about the uploaded PDF |
| GET | `/history/{session_id}` | Retrieve chat history for a session |
| GET | `/sessions` | List all chat sessions |

---

## Example Usage

**Upload a PDF:**
```bash
curl -X POST https://llm-api-production-production.up.railway.app/upload \
  -F "file=@document.pdf"
```

Response:
```json
{
  "message": "Successfully processed document.pdf",
  "pages": 15,
  "chunks": 52
}
```

**Ask a question:**
```bash
curl -X POST https://llm-api-production-production.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the Transformer?", "session_id": "my-session"}'
```

Response:
```json
{
  "answer": "The Transformer is a model architecture that eschews recurrence and instead relies entirely on an attention mechanism...",
  "session_id": "my-session",
  "sources": ["...relevant chunk 1...", "...relevant chunk 2..."]
}
```

**Get chat history:**
```bash
curl https://llm-api-production-production.up.railway.app/history/my-session
```

---

## Tech Stack

- **FastAPI** — REST API framework with automatic Swagger docs
- **LangChain** — RAG pipeline and LLM integration
- **Google Gemini** — LLM for answering questions + embeddings
- **ChromaDB** — Vector database for storing document embeddings
- **Langfuse** — LLM observability and tracing
- **Supabase** — PostgreSQL database for persistent chat history
- **Railway** — Cloud deployment platform
- **Python-dotenv** — Environment variable management

---

## Architecture

```
POST /upload
    ↓
PyPDFLoader → RecursiveCharacterTextSplitter
    ↓
GeminiEmbeddings (gemini-embedding-001)
    ↓
ChromaDB (vector store)

POST /chat
    ↓
ChromaDB retriever (top 3 chunks)
    ↓
Gemini (gemini-2.5-flash) → answer
    ↓
Supabase (save user + assistant messages)
    ↓
Langfuse (log trace)
```

---

## File Structure

```
llm-api-production/
├── main.py          # FastAPI app and endpoints
├── rag.py           # RAG logic with Langfuse tracing
├── database.py      # Supabase chat history
├── schemas.py       # Pydantic request/response models
├── requirements.txt # Dependencies
├── .env.example     # Template for required environment variables
├── .python-version  # Python 3.12 for Railway
├── .env             # API keys (not on GitHub)
└── .gitignore
```

---

## Key Concepts

| Concept | What It Means |
|---------|--------------|
| RAG | Retrieve relevant document chunks before asking the LLM — reduces hallucinations |
| Vector embeddings | Text converted to numbers so similarity search works |
| ChromaDB | Local vector store — stores and retrieves embeddings |
| Langfuse | Logs every LLM call with inputs, outputs, latency, and cost |
| Supabase | Cloud PostgreSQL — persists chat history across sessions |
| Session ID | Groups messages together so history is retrievable per user |

---

## Run Locally

**Prerequisites:** Python 3.12, pip

```bash
# Clone the repo
git clone https://github.com/richardy-lobo-sapan/llm-api-production.git
cd llm-api-production

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# Install dependencies
# (Windows only: ChromaDB requires a pre-built greenlet binary)
pip install greenlet --only-binary=:all:
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Open .env and fill in your API keys

# Run the API
uvicorn main:app --reload

# Open docs
http://127.0.0.1:8000/docs
```

Get free API keys:
- Gemini: https://aistudio.google.com/apikey
- Langfuse: https://us.cloud.langfuse.com
- Supabase: https://supabase.com

---

## Limitations

- **One document at a time** — uploading a new PDF replaces the previous one in the vector store. Session chat history in Supabase is preserved, but the document context resets.
- ChromaDB is stored in memory/locally; restarting the server clears the vector store (re-upload your PDF after a restart).

---

## What Makes This Production-Ready

| Feature | Why It Matters |
|---------|---------------|
| Persistent storage | Chat history survives server restarts |
| Observability | Every LLM call is traceable — debug and monitor in production |
| Session management | Multiple users can have separate conversations |
| Error handling | API returns proper HTTP errors instead of crashing |
| CORS middleware | Frontend apps can call the API from any domain |
| Docker-compatible | Runs consistently across environments |
| CI/CD via Railway | Auto-deploys on every git push |

---

## Author

**Richardy Lobo' Sapan**
- GitHub: [@richardy-lobo-sapan](https://github.com/richardy-lobo-sapan)
- LinkedIn: [richardylobosapan](https://www.linkedin.com/in/richardylobosapan/)

Found a bug or have a question? [Open an issue](https://github.com/richardy-lobo-sapan/llm-api-production/issues).
