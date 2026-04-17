const API_BASE = process.env.FASTAPI_URL || "http://localhost:8000"

export async function POST(req: Request) {
  const body = await req.json()

  const upstream = await fetch(`${API_BASE}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
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
