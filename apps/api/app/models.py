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


class ChatRequest(BaseModel):
    message: str
    session_id: str
    project_id: str
    model: str = "claude-sonnet-4-5-20250514"


class ChatResponse(BaseModel):
    content: str
    tool_calls: list[ToolCall] | None = None
    done: bool = True


# ─── Scan ───────────────────────────────────────────────────


class ScanRequest(BaseModel):
    scan_id: str
    tool: str
    target: str
    args: dict = {}
    project_id: str


class ScanResult(BaseModel):
    scan_id: str
    status: ScanStatus
    output: str | None = None
    error: str | None = None
    findings: list[dict] = []
