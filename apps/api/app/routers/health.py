"""Health check router."""

from fastapi import APIRouter

from app.config import settings
from app.tools import tool_registry

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    available_tools = tool_registry.list_available()
    return {
        "status": "ok",
        "app": settings.app_name,
        "tools_registered": len(tool_registry.list_all()),
        "tools_available": len(available_tools),
    }
