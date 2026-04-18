"""Scan router — POST /api/scan, GET /api/tools, GET /api/scan/{task_id}/status"""

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException

from app.auth import AuthenticatedUser, get_current_user
from app.celery_app import celery
from app.models import ScanRequest, ScanResult, ScanStatus
from app.tasks import execute_tool
from app.tools import tool_registry

router = APIRouter(prefix="/api", tags=["scan"])


@router.get("/tools")
async def list_tools(user: AuthenticatedUser = Depends(get_current_user)):
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
async def run_scan(
    req: ScanRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> ScanResult:
    """Submit a scan to Celery for background execution.

    Returns immediately with PENDING status and a task_id for polling.
    """
    tool = tool_registry.get(req.tool)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{req.tool}' not found.")

    if not tool.is_available():
        raise HTTPException(
            status_code=503,
            detail=f"Tool '{req.tool}' is not installed on the server.",
        )

    task = execute_tool.delay(req.tool, {"target": req.target, **req.args})

    return ScanResult(
        scan_id=req.scan_id,
        task_id=task.id,
        status=ScanStatus.PENDING,
    )


@router.get("/scan/{task_id}/status")
async def scan_status(
    task_id: str,
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Poll the status of a Celery scan task."""
    result = AsyncResult(task_id, app=celery)

    if result.state == "PENDING":
        return {"task_id": task_id, "status": "PENDING"}

    if result.state == "RUNNING" or result.state == "STARTED":
        return {"task_id": task_id, "status": "RUNNING"}

    if result.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "FAILED",
            "error": str(result.result),
        }

    if result.state == "SUCCESS":
        data = result.result
        return {
            "task_id": task_id,
            "status": "COMPLETED",
            "output": (data.get("output") or "")[:10000],
            "error": data.get("error"),
            "findings": data.get("findings", []),
        }

    return {"task_id": task_id, "status": result.state}
