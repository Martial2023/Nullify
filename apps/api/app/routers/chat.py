"""Chat router — POST /api/chat"""

from fastapi import APIRouter, HTTPException

from app.models import ChatRequest, ChatResponse
from app.services.llm import chat_with_tools

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """Process a chat message through Claude with security tools."""
    try:
        response = await chat_with_tools(
            message=req.message,
            model=req.model,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
