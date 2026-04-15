import type { MessageRole } from "./enums";

export interface ChatSession {
  id: string;
  title: string | null;
  projectId: string;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ToolCall {
  id: string;
  name: string;
  args: Record<string, unknown>;
  result?: string;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  toolCalls: ToolCall[] | null;
  sessionId: string;
  createdAt: Date;
}

export interface ChatSessionWithMessages extends ChatSession {
  messages: Message[];
}
