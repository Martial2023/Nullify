import type { ToolCall } from "./chat";

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  message: string;
  code?: string;
}

export interface ChatRequest {
  message: string;
  sessionId: string;
  projectId: string;
  model: string;
}

export interface ChatResponse {
  content: string;
  toolCalls?: ToolCall[];
  done: boolean;
}

export type SSEEventType =
  | "thinking"
  | "tool_start"
  | "tool_output"
  | "message"
  | "error"
  | "done"

export interface SSEEvent {
  event: SSEEventType
  content?: string
  tool_call_id?: string
  name?: string
  args?: Record<string, unknown>
  result?: string
  tool_calls?: ToolCall[]
}
