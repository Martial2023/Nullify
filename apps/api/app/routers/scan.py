"""Scan router — POST /api/scan, GET /api/tools"""

from fastapi import APIRouter, HTTPException

from app.models import ScanRequest, ScanResult, ScanStatus
from app.tools import tool_registry

router = APIRouter(prefix="/api", tags=["scan"])


@router.get("/tools")
async def list_tools():
    """List all registered security tools and their availability."""
    return [
        {
            "name": t.name,
            "description": t.description,
            "available": t.is_available(),
        }
        for t in tool_registry.list_all()
    ]


@router.post("/scan", response_model=ScanResult)
async def run_scan(req: ScanRequest) -> ScanResult:
    """Execute a security tool scan directly (without AI)."""
    tool = tool_registry.get(req.tool)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{req.tool}' not found.")

    if not tool.is_available():
        raise HTTPException(
            status_code=503,
            detail=f"Tool '{req.tool}' is not installed on the server.",
        )

    result = await tool.execute({"target": req.target, **req.args})

    return ScanResult(
        scan_id=req.scan_id,
        status=ScanStatus.COMPLETED if result.success else ScanStatus.FAILED,
        output=result.output[:10000] if result.output else None,
        error=result.error,
        findings=result.findings,
    )
