"""Pydantic models — miroir des types TypeScript du frontend."""

from enum import Enum

from pydantic import BaseModel


# ─── Enums ──────────────────────────────────────────────────


class MessageRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    TOOL = "TOOL"


class ScanStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


# ─── Chat ───────────────────────────────────────────────────


class ToolCall(BaseModel):
    id: str
    name: str
    args: dict
    result: str | None = None


class HistoryMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: str
    project_id: str
    model: str = "claude-sonnet-4-5-20250514"
    history: list[HistoryMessage] | None = None


class ChatResponse(BaseModel):
    content: str
    tool_calls: list[ToolCall] | None = None
    done: bool = True


# ─── SSE Streaming ─────────────────────────────────────────


class SSEEventType(str, Enum):
    THINKING = "thinking"
    TOOL_START = "tool_start"
    TOOL_OUTPUT = "tool_output"
    MESSAGE = "message"
    ERROR = "error"
    DONE = "done"


class SSEEvent(BaseModel):
    event: SSEEventType
    content: str | None = None
    tool_call_id: str | None = None
    name: str | None = None
    args: dict | None = None
    result: str | None = None
    findings: list[dict] | None = None
    tool_calls: list[ToolCall] | None = None


# ─── Scan ───────────────────────────────────────────────────


class ScanRequest(BaseModel):
    scan_id: str
    tool: str
    target: str
    args: dict = {}
    project_id: str


class ScanResult(BaseModel):
    scan_id: str
    task_id: str | None = None
    status: ScanStatus
    output: str | None = None
    error: str | None = None
    findings: list[dict] = []