from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chatbot import chat_with_rag

router = APIRouter(prefix="/api", tags=["chatbot"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the HealthTwin AI medical assistant powered by RAG + Groq."""
    result = await chat_with_rag(
        user_message=request.message,
        history=request.history,
    )
    return ChatResponse(**result)
