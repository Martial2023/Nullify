import { cookies } from "next/headers"

const API_BASE = process.env.FASTAPI_URL || "http://localhost:8000"

export async function POST(req: Request) {
  // Extract Better-Auth session token from cookie
  // In production (HTTPS), Better-Auth prefixes with __Secure-
  const cookieStore = await cookies()
  const sessionToken =
    cookieStore.get("better-auth.session_token")?.value ??
    cookieStore.get("__Secure-better-auth.session_token")?.value

  if (!sessionToken) {
    return new Response(
      JSON.stringify({ error: "Not authenticated" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    )
  }

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
