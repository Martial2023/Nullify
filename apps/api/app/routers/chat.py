"""Chat router — POST /api/chat + POST /api/chat/stream (SSE)"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.auth import AuthenticatedUser, get_current_user
from app.models import ChatRequest, ChatResponse
from app.services.llm import chat_with_tools, chat_with_tools_stream
from app.agents import agent_registry

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> ChatResponse:
    """Non-streaming chat — kept for backwards compatibility."""
    try:
        return await chat_with_tools(
            message=req.message, model=req.model, history=req.history,
            agent=req.agent,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(
    req: ChatRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """SSE streaming chat — real-time tool execution events."""

    async def event_generator():
        async for event in chat_with_tools_stream(
            message=req.message, model=req.model, history=req.history,
            agent=req.agent,
        ):
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        },
    )


@router.get("/agents")
async def list_agents(
    user: AuthenticatedUser = Depends(get_current_user),
):
    """List all available security agents."""
    agents = agent_registry.list_all()
    return [
        {
            "name": a.name,
            "description": a.description,
            "tools": a.get_tools(),
        }
        for a in agents
    ]
