"""LLM service — OpenRouter API with tool_use, SSE streaming."""

import asyncio
import json
from collections.abc import AsyncGenerator

import httpx

from app.config import settings
from app.models import ChatResponse, HistoryMessage, SSEEvent, SSEEventType, ToolCall
from app.tasks import execute_tool
from app.tools import tool_registry

SYSTEM_PROMPT = """\
You are Nullify, an AI Security Engineer. You help users perform security \
assessments by orchestrating security tools.

Your capabilities:
- Reconnaissance: subdomain discovery, port scanning, HTTP probing
- Vulnerability scanning: CVE detection, misconfiguration checks
- Analysis: interpret results, prioritize findings, suggest remediation

Guidelines:
- Always confirm the target scope before scanning.
- Use tools in a logical order: recon first, then targeted scans.
- Explain what each tool does before running it.
- After receiving tool results, provide a clear summary with severity ratings.
- If a tool is not available, explain what it would do and suggest alternatives.
- Be concise but thorough in your analysis.
- Flag critical and high severity findings prominently.
"""

MODEL_MAP: dict[str, str] = {
    "claude-opus-4-5": "anthropic/claude-opus-4",
    "claude-sonnet-4-5": "anthropic/claude-sonnet-4-5",
    "claude-haiku-4-5": "anthropic/claude-haiku-4-5",
    "gpt-5-1-codex": "openai/gpt-4.1",
    "gpt-5-1": "openai/gpt-4.1",
    "gemini-3-0-pro": "google/gemini-2.5-pro-preview",
    "kimi-k2-thinking": "moonshotai/kimi-k2",
    "grok-4-1-fast": "x-ai/grok-3-fast",
}


def _resolve_model(model_id: str) -> str:
    return MODEL_MAP.get(model_id, settings.default_model)


def _tools_to_openai_format(tools: list[dict]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            },
        }
        for t in tools
    ]


async def _execute_tool_direct(tool_name: str, tool_args: dict, timeout: int = 600) -> dict:
    """Execute a tool directly (no Celery)."""
    tool = tool_registry.get(tool_name)
    if tool is None:
        return {"success": False, "output": "", "error": f"Tool '{tool_name}' not found.", "findings": []}
    result = await tool.execute(tool_args, timeout=timeout)
    return {"success": result.success, "output": result.output, "error": result.error, "findings": result.findings}


def _celery_workers_available() -> bool:
    """Check if at least one Celery worker is online. Returns False on any error."""
    try:
        from app.celery_app import celery as celery_app
        inspect = celery_app.control.inspect(timeout=2.0)
        ping = inspect.ping()
        return bool(ping)
    except Exception:
        return False


async def _execute_tool_celery(
    tool_name: str, tool_args: dict, timeout: int = 600, poll_interval: float = 2.0
) -> dict:
    """Dispatch tool execution to a Celery worker and poll for the result.

    Falls back to direct execution if no Celery worker is available.
    """
    # Check if workers are online before dispatching
    has_workers = await asyncio.to_thread(_celery_workers_available)
    if not has_workers:
        return await _execute_tool_direct(tool_name, tool_args, timeout)

    try:
        task: AsyncResult = execute_tool.delay(tool_name, tool_args, timeout)
    except Exception:
        return await _execute_tool_direct(tool_name, tool_args, timeout)

    elapsed = 0.0
    while elapsed < timeout + 60:
        if task.ready():
            break
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval

    if not task.ready():
        task.revoke(terminate=True)
        return {"success": False, "output": "", "error": f"Task timed out ({timeout}s).", "findings": []}

    if task.failed():
        return {"success": False, "output": "", "error": str(task.result), "findings": []}

    return task.result


async def chat_with_tools_stream(
    message: str,
    model: str,
    history: list[HistoryMessage] | None = None,
) -> AsyncGenerator[SSEEvent, None]:
    """Agentic tool-use loop, yielding SSE events as things happen."""

    raw_tools = tool_registry.to_claude_tools()
    openai_tools = _tools_to_openai_format(raw_tools) if raw_tools else []
    resolved_model = _resolve_model(model)

    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(
            {"role": h.role.lower(), "content": h.content} for h in history
        )
    messages.append({"role": "user", "content": message})

    collected_tool_calls: list[ToolCall] = []

    async with httpx.AsyncClient(timeout=httpx.Timeout(300, connect=10)) as client:
        while True:
            payload: dict = {
                "model": resolved_model,
                "messages": messages,
                "max_tokens": 4096,
            }
            if openai_tools:
                payload["tools"] = openai_tools

            try:
                resp = await client.post(
                    f"{settings.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "Nullify",
                    },
                    json=payload,
                )
                resp.raise_for_status()
            except Exception as e:
                yield SSEEvent(event=SSEEventType.ERROR, content=str(e))
                yield SSEEvent(event=SSEEventType.DONE)
                return

            data = resp.json()
            choice = data["choices"][0]
            assistant_msg = choice["message"]
            finish_reason = choice.get("finish_reason", "stop")

            # --- Tool calls requested by the LLM ---
            if finish_reason == "tool_calls" or assistant_msg.get("tool_calls"):
                # If the LLM included reasoning text, stream it
                if assistant_msg.get("content"):
                    yield SSEEvent(
                        event=SSEEventType.THINKING,
                        content=assistant_msg["content"],
                    )

                messages.append(assistant_msg)

                for tc in assistant_msg.get("tool_calls", []):
                    fn = tc["function"]
                    tool_name = fn["name"]
                    tool_args = (
                        json.loads(fn["arguments"])
                        if isinstance(fn["arguments"], str)
                        else fn["arguments"]
                    )
                    tool_id = tc["id"]

                    # Notify: tool is starting
                    yield SSEEvent(
                        event=SSEEventType.TOOL_START,
                        tool_call_id=tool_id,
                        name=tool_name,
                        args=tool_args,
                    )

                    # Execute the tool via Celery worker
                    tool = tool_registry.get(tool_name)
                    tool_findings: list[dict] = []
                    if tool:
                        result_dict = await _execute_tool_celery(
                            tool_name, tool_args
                        )
                        result_text = (
                            result_dict["output"]
                            if result_dict["success"]
                            else (result_dict["error"] or "Tool execution failed.")
                        )
                        tool_findings = result_dict["findings"]
                    else:
                        result_text = f"Tool '{tool_name}' is not available."

                    # Notify: tool finished
                    yield SSEEvent(
                        event=SSEEventType.TOOL_OUTPUT,
                        tool_call_id=tool_id,
                        name=tool_name,
                        result=result_text[:5000],
                        findings=tool_findings if tool_findings else None,
                    )

                    collected_tool_calls.append(
                        ToolCall(
                            id=tool_id,
                            name=tool_name,
                            args=tool_args,
                            result=result_text[:5000],
                        )
                    )

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "content": result_text[:5000],
                    })

                # Loop back to let the LLM process results
                continue

            # --- Final text response ---
            final_text = assistant_msg.get("content", "") or ""
            yield SSEEvent(event=SSEEventType.MESSAGE, content=final_text)
            yield SSEEvent(
                event=SSEEventType.DONE,
                tool_calls=collected_tool_calls if collected_tool_calls else None,
            )
            return


async def chat_with_tools(
    message: str,
    model: str,
    history: list[HistoryMessage] | None = None,
) -> ChatResponse:
    """Non-streaming wrapper — keeps the old POST /api/chat working."""
    final_content = ""
    final_tool_calls: list[ToolCall] | None = None

    async for event in chat_with_tools_stream(message, model, history):
        if event.event == SSEEventType.MESSAGE:
            final_content = event.content or ""
        elif event.event == SSEEventType.DONE:
            final_tool_calls = event.tool_calls

    return ChatResponse(
        content=final_content,
        tool_calls=final_tool_calls,
        done=True,
    )
