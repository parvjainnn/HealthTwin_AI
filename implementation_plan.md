# Implement RAG Chatbot in HealthTwin (Migrating from medical-chatbot)

Replace the existing Ollama-based chatbot in the HealthTwin app with a RAG (Retrieval-Augmented Generation) chatbot identical to the `medical-chatbot` project. The RAG pipeline uses **FAISS** vectorstore, **HuggingFace** embeddings (`all-MiniLM-L6-v2`), **Groq** LLM (`llama-3.1-8b-instant`), and **LangChain** retrieval chains.

## User Review Required

> [!IMPORTANT]
> **GROQ_API_KEY required**: You will need to set your Groq API key in the [.env](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/medical-chatbot/.env) file at the project root for the chatbot to work. The plan assumes the key from [medical-chatbot/.env](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/medical-chatbot/.env) is valid.

> [!NOTE]
> The existing FAISS vectorstore at `medical-chatbot/vectorstore/db_faiss` will be reused as-is — no re-indexing needed. All required Python packages (`langchain`, `langchain-groq`, `langchain-huggingface`, `faiss-cpu`, etc.) are already in `requirements.txt`.

---

## Proposed Changes

### Backend Service

#### [MODIFY] [chatbot.py](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/services/chatbot.py)

Complete rewrite. Replace Ollama HTTP calls with the RAG pipeline from `medibot.py`:
- Load FAISS vectorstore using HuggingFace embeddings on module init
- Create Groq LLM client with `llama-3.1-8b-instant`
- Build RAG chain using `create_retrieval_chain` + `create_stuff_documents_chain`
- Pull the `langchain-ai/retrieval-qa-chat` prompt
- Return answer + source document metadata
- Keep the function async-compatible by wrapping sync LangChain calls with `asyncio.to_thread`

---

### Schemas

#### [MODIFY] [schemas.py](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/models/schemas.py)

- Add `SourceDocument` model (page content snippet, metadata)  
- Update `ChatResponse` to include optional `sources: List[SourceDocument]`

---

### Router

#### [MODIFY] [chatbot.py](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/routers/chatbot.py)

- Pass through sources from the service response to the API response

---

### App Initialization

#### [MODIFY] [main.py](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/main.py)

- Load `.env` using `dotenv` at startup so `GROQ_API_KEY` is available

---

### Environment

#### [NEW] [.env](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/.env)

- Copy `GROQ_API_KEY` from `medical-chatbot/.env`
- Set `HF_TOKEN` if needed

---

### Frontend

#### [MODIFY] [index.html](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/static/index.html)

- Update chatbot section subtitle from "powered by Ollama" to "powered by RAG & Groq AI"

#### [MODIFY] [app.js](file:///c:/Users/ASUS/Documents/WebD/HackathonProject/healthtwin/app/static/js/app.js)

- Update `sendChat()` error message to remove Ollama reference
- Display source documents (collapsible) below the assistant reply when returned

---

## Verification Plan

### Manual Verification
1. Start the server: `cd healthtwin && python -m uvicorn app.main:app --reload`
2. Open `http://localhost:8000` in the browser
3. Navigate to the "💬 AI Chat" section
4. Send the message "What is diabetes?"
5. Verify the bot responds with a relevant medical answer (not an Ollama error)
6. Verify source references appear below the response
7. Send a follow-up message and confirm conversational context is maintained
