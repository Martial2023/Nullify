import type { ChatRequest, ChatResponse } from "@/types"

const API_BASE = process.env.FASTAPI_URL || "http://localhost:8000"

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  })

  if (!res.ok) {
    const body = await res.text().catch(() => "Unknown error")
    throw new Error(`FastAPI ${res.status}: ${body}`)
  }

  return res.json() as Promise<T>
}

export const fastapiClient = {
  async chat(req: ChatRequest): Promise<ChatResponse> {
    const raw = await apiFetch<{
      content: string
      tool_calls?: { id: string; name: string; args: Record<string, unknown>; result?: string }[]
      done: boolean
    }>("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        message: req.message,
        session_id: req.sessionId,
        project_id: req.projectId,
        model: req.model,
      }),
    })

    return {
      content: raw.content,
      toolCalls: raw.tool_calls,
      done: raw.done,
    }
  },

  async runScan(
    tool: string,
    target: string,
    args: Record<string, unknown> = {},
    scanId?: string
  ): Promise<{ status: string }> {
    const result = await apiFetch<{ status: string }>("/api/scan", {
      method: "POST",
      body: JSON.stringify({
        scan_id: scanId || crypto.randomUUID(),
        tool,
        target,
        args,
        project_id: "",
      }),
    })
    return result
  },

  async generateReport(
    _projectId: string
  ): Promise<{ summary: string; content: object | null }> {
    // TODO: implémenter côté FastAPI dans une phase ultérieure
    return {
      summary: "Report generation not yet implemented on backend.",
      content: null,
    }
  },

  async listTools(): Promise<
    { name: string; description: string; available: boolean }[]
  > {
    return apiFetch("/api/tools")
  },
}
