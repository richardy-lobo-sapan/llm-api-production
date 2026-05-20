import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from langfuse import Langfuse
from google import genai
from typing import List

load_dotenv()

# Langfuse client
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# Custom Gemini embeddings
class GeminiEmbeddings(Embeddings):
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = "models/gemini-embedding-001"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            result = self.client.models.embed_content(
                model=self.model, contents=text)
            embeddings.append(result.embeddings[0].values)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        result = self.client.models.embed_content(
            model=self.model, contents=text)
        return result.embeddings[0].values

# Global vectorstore
vectorstore = None

def process_pdf(file_path: str):
    global vectorstore

    loader = PyPDFLoader(file_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(pages)

    embeddings = GeminiEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    return len(pages), len(chunks)

def answer_question(question: str, session_id: str = "default"):
    global vectorstore

    if not vectorstore:
        return "No document loaded. Please upload a PDF first.", []

    # Retrieve relevant chunks
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    sources = retriever.invoke(question)

    # Build context
    context = "\n\n".join([doc.page_content for doc in sources])

    # Generate answer with Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )

    prompt = f"Answer the question using only the context below.\n\nContext:\n{context}\n\nQuestion: {question}"

    # Log to Langfuse using new v3 API
    with langfuse.start_as_current_span(name="rag-query") as span:
        span.update(input=question, metadata={"session_id": session_id})
        response = llm.invoke(prompt)
        answer = response.content
        span.update(output=answer)

    source_texts = [doc.page_content[:200] for doc in sources]
    return answer, source_texts