import type { AIModel } from "@/types"

export const AI_MODELS: AIModel[] = [
  { id: "claude-opus-4-5", name: "Claude Opus 4.5", provider: "Anthropic" },
  { id: "claude-sonnet-4-5", name: "Claude Sonnet 4.5", provider: "Anthropic" },
  { id: "claude-haiku-4-5", name: "Claude Haiku 4.5", provider: "Anthropic" },
  { id: "gpt-5-1-codex", name: "GPT-5.1 Codex", provider: "OpenAI" },
  { id: "gpt-5-1", name: "GPT 5.1", provider: "OpenAI" },
  { id: "gemini-3-0-pro", name: "Gemini 3.0 Pro", provider: "Google" },
  { id: "kimi-k2-thinking", name: "Kimi K2 Thinking", provider: "Moonshot" },
  { id: "grok-4-1-fast", name: "Grok 4.1 Fast", provider: "xAI" },
]

export const DEFAULT_MODEL_ID = "claude-opus-4-5"

export function getModelById(id: string) {
  return AI_MODELS.find((m) => m.id === id)
}
