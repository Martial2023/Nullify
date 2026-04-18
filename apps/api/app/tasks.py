"""Celery tasks — long-running tool execution in background workers."""

import asyncio

from celery.signals import worker_init

from app.celery_app import celery
from app.tools import tool_registry
from app.tools.base import SecurityTool
from app.tools.httpx_tool import HttpxTool
from app.tools.nmap import NmapTool
from app.tools.nuclei import NucleiTool
from app.tools.subfinder import SubfinderTool


@worker_init.connect
def register_tools(**_kwargs):
    """Register security tools when the Celery worker starts."""
    if not tool_registry.list_all():
        tool_registry.register(NmapTool())
        tool_registry.register(SubfinderTool())
        tool_registry.register(HttpxTool())
        tool_registry.register(NucleiTool())
        available = tool_registry.list_available()
        print(f"[Worker] {len(tool_registry.list_all())} tools registered, {len(available)} available")


def _run_tool_sync(tool: SecurityTool, args: dict, timeout: int) -> dict:
    """Run an async tool.execute() from a sync Celery worker."""
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(tool.execute(args, timeout=timeout))
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "findings": result.findings,
        }
    finally:
        loop.close()


@celery.task(bind=True, name="app.tasks.execute_tool", time_limit=660, soft_time_limit=600)
def execute_tool(self, tool_name: str, tool_args: dict, timeout: int = 600) -> dict:
    """Execute a security tool inside Docker.

    Returns a serializable dict matching ToolResult fields.
    Raises if the tool is not found or not available.
    """
    tool = tool_registry.get(tool_name)
    if tool is None:
        return {
            "success": False,
            "output": "",
            "error": f"Tool '{tool_name}' not found.",
            "findings": [],
        }

    if not tool.is_available():
        return {
            "success": False,
            "output": "",
            "error": f"Tool '{tool_name}' is not available (Docker not found).",
            "findings": [],
        }

    self.update_state(state="RUNNING", meta={"tool": tool_name})
    return _run_tool_sync(tool, tool_args, timeout)
