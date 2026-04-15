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
