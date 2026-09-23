# backend/app/routes/chatbot.py
"""
Routes du chatbot intelligent.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

from app.services.chatbot_service import get_chatbot_response, get_llm_status

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


class ChatMessage(BaseModel):
    role: str  # "user" ou "assistant"
    content: str


class ChatRequest(BaseModel):
    question: str
    profile: Optional[Dict] = None
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    source: str
    llm_enabled: bool


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chatbot carrière intelligent avec LLM."""
    try:
        history = [msg.dict() for msg in request.history] if request.history else []
        result = get_chatbot_response(
            question=request.question,
            profile=request.profile,
            history=history,
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def chatbot_status():
    """Statut du chatbot (LLM activé ou non)."""
    return get_llm_status()