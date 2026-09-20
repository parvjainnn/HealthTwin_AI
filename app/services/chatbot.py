import asyncio
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── Paths ────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_FAISS_PATH = str(PROJECT_ROOT / "medical-chatbot" / "vectorstore" / "db_faiss")

# ── System prompt ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are HealthTwin AI, a knowledgeable and empathetic medical assistant.
Use the following retrieved context to answer the user's health question.
If you don't know the answer based on the context, say so honestly.
Always recommend consulting a healthcare professional for diagnosis and treatment.

Context:
{context}"""

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])

# ── Globals with ASYNC-safe locking ─────────────────────────
_vectorstore = None
_rag_chain = None
_init_lock = asyncio.Lock()  # FIX: async-safe, never blocks the event loop


def _build_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def _build_vectorstore():
    """Pure sync — only call from inside asyncio.to_thread."""
    faiss_path = Path(DB_FAISS_PATH)
    if not faiss_path.exists():
        raise FileNotFoundError(
            f"FAISS vector store not found at: {DB_FAISS_PATH}\n"
            "Please run the ingestion script first to build the vector store."
        )
    embedding_model = _build_embedding_model()
    return FAISS.load_local(
        DB_FAISS_PATH,
        embedding_model,
        allow_dangerous_deserialization=True,
    )


def _build_rag_chain(vectorstore):
    """Pure sync — only call from inside asyncio.to_thread."""
    llm = ChatOllama(
        model="llama3.2",
        temperature=0.5,
        timeout=120,        # FIX: won't hang forever; raises TimeoutError after 120s
        num_predict=512,    # cap output tokens to avoid very long waits
    )
    combine_docs_chain = create_stuff_documents_chain(llm, RAG_PROMPT)
    return create_retrieval_chain(
        vectorstore.as_retriever(search_kwargs={"k": 3}),
        combine_docs_chain,
    )


async def _ensure_initialized():
    """
    Lazily initialise vectorstore + RAG chain using an async lock.
    Safe to call concurrently from multiple FastAPI requests.
    """
    global _vectorstore, _rag_chain

    if _rag_chain is not None:  # fast path
        return

    async with _init_lock:      # FIX: awaited lock — event loop stays free
        if _rag_chain is not None:  # double-check after acquiring
            return

        print("Initialising vectorstore and RAG chain (first request)...")
        vs    = await asyncio.to_thread(_build_vectorstore)
        chain = await asyncio.to_thread(_build_rag_chain, vs)
        _vectorstore = vs
        _rag_chain   = chain
        print("RAG chain ready.")


def _invoke_rag(user_message: str, history: list[dict] | None, chain) -> dict:
    """
    Pure sync RAG call — runs inside asyncio.to_thread.
    Receives the already-built chain so no lazy-init happens here.
    """
    if history:
        recent = history[-4:]
        history_text = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in recent
        )
        enriched_input = f"Conversation so far:\n{history_text}\n\nUser: {user_message}"
    else:
        enriched_input = user_message

    response = chain.invoke({"input": enriched_input})

    sources = []
    for doc in response.get("context", []):
        snippet = doc.page_content[:300]
        last_period = snippet.rfind(".")
        if last_period > 100:
            snippet = snippet[: last_period + 1]
        sources.append({
            "content": snippet,
            "metadata": {k: str(v) for k, v in doc.metadata.items()},
        })

    return {
        "reply": response.get("answer", "I couldn't generate a response."),
        "model": "llama3.2 (Ollama + RAG)",
        "sources": sources,
    }


async def chat_with_rag(user_message: str, history: list[dict] = None) -> dict:
    """Main async entry point for FastAPI routes."""
    try:
        await _ensure_initialized()
        result = await asyncio.to_thread(_invoke_rag, user_message, history, _rag_chain)
        return result

    except FileNotFoundError as e:
        return {"reply": f"Setup Error: {e}", "model": "llama3.2 (Ollama + RAG)", "sources": []}
    except TimeoutError:
        return {
            "reply": "The model took too long to respond. Ollama may still be loading llama3.2 — please retry.",
            "model": "llama3.2 (Ollama + RAG)",
            "sources": [],
        }
    except Exception as e:
        return {"reply": f"RAG Error: {e}", "model": "llama3.2 (Ollama + RAG)", "sources": []}


# ── Document ingestion ────────────────────────────────────────

def _ingest_sync(file_path: str) -> bool:
    try:
        path = Path(file_path)
        loader = PyPDFLoader(str(path)) if path.suffix.lower() == ".pdf" else TextLoader(str(path))
        docs = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        ).split_documents(loader.load())

        vs = _vectorstore or _build_vectorstore()
        vs.add_documents(docs)
        vs.save_local(DB_FAISS_PATH)
        # No _rag_chain reset needed — FAISS in-memory store is already updated
        return True
    except Exception as e:
        print(f"Error ingesting document: {e}")
        return False


async def ingest_document(file_path: str) -> bool:
    return await asyncio.to_thread(_ingest_sync, file_path)