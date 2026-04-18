import { headers } from "next/headers"
import { auth } from "@/lib/auth"

const API_BASE = process.env.FASTAPI_URL || "http://localhost:8000"

export async function POST(req: Request) {
  // Validate session via Better-Auth (handles cookie name internally)
  const session = await auth.api.getSession({
    headers: await headers(),
  })

  if (!session?.session) {
    return new Response(
      JSON.stringify({ error: "Not authenticated" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    )
  }

  const sessionToken = session.session.token

  const body = await req.json()

  const upstream = await fetch(`${API_BASE}/api/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${sessionToken}`,
    },
    body: JSON.stringify(body),
  })

  if (!upstream.ok || !upstream.body) {
    return new Response(
      JSON.stringify({ error: `FastAPI ${upstream.status}` }),
      { status: upstream.status, headers: { "Content-Type": "application/json" } }
    )
  }

  return new Response(upstream.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  })
}
