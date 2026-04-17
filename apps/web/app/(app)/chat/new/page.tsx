"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { PanelLeft, PanelRight } from "lucide-react"
import { createProject } from "@/app/(actions)/project"
import { createChatSession, persistUserMessage, persistAssistantMessage } from "@/app/(actions)/chat"
import { DEFAULT_MODEL_ID } from "@/lib/models"
import type { Message } from "@/types"
import type { SSEEvent } from "@/types/api"
import { MessageList } from "../_components/message-list"
import { ChatInput } from "../_components/chat-input"
import { ChatEmptyState } from "../_components/chat-empty-state"

function generateProjectName(message: string): string {
  const cleaned = message.replace(/\s+/g, " ").trim()
  if (cleaned.length <= 50) return cleaned
  return cleaned.slice(0, 47) + "..."
}

export default function NewChatPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [modelId, setModelId] = useState(DEFAULT_MODEL_ID)
  const [sending, setSending] = useState(false)

  const handleSend = async (content: string) => {
    // Show user message immediately
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "USER",
      content,
      toolCalls: null,
      sessionId: "",
      createdAt: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])
    setSending(true)

    try {
      // 1. Create project + session
      const project = await createProject({
        name: generateProjectName(content),
      })
      const session = await createChatSession(project.id, generateProjectName(content))

      // 2. Persist user message
      await persistUserMessage(session.id, content)

      // 3. Stream from FastAPI via Next.js proxy
      const resp = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: content,
          session_id: session.id,
          project_id: project.id,
          model: modelId,
        }),
      })

      if (!resp.ok || !resp.body) {
        throw new Error(`Stream error: ${resp.status}`)
      }

      // 4. Placeholder assistant message
      const assistantId = crypto.randomUUID()
      setMessages((prev) => [
        ...prev,
        {
          id: assistantId,
          role: "ASSISTANT" as const,
          content: "",
          toolCalls: null,
          sessionId: session.id,
          createdAt: new Date(),
        },
      ])

      // 5. Read SSE stream
      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""
      let finalContent = ""
      let collectedToolCalls: Message["toolCalls"] | undefined

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() ?? ""

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          const json = line.slice(6).trim()
          if (!json) continue

          let event: SSEEvent
          try {
            event = JSON.parse(json)
          } catch {
            continue
          }

          if (event.event === "message" || event.event === "thinking") {
            if (event.event === "message") {
              finalContent = event.content ?? ""
            } else {
              finalContent += event.content ?? ""
            }
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, content: finalContent } : m
              )
            )
          } else if (event.event === "done") {
            collectedToolCalls = event.tool_calls ?? undefined
          } else if (event.event === "error") {
            finalContent = `Error: ${event.content ?? "Unknown error"}`
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, content: finalContent } : m
              )
            )
          }
        }
      }

      // 6. Persist assistant message
      await persistAssistantMessage(session.id, finalContent, collectedToolCalls ?? undefined)

      // Redirect to the real chat page
      router.replace(`/chat/${project.id}`)
    } catch (error) {
      console.error("Failed to create chat:", error)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="flex h-[calc(100vh-3rem)] flex-col">
      <div className="flex items-center justify-between px-4 py-2">
        <Button variant="ghost" size="sm" disabled className="gap-1.5">
          <PanelLeft className="size-4" />
          <span className="hidden sm:inline">Context</span>
        </Button>
        <span className="text-sm font-medium">New Chat</span>
        <Button variant="ghost" size="sm" disabled className="gap-1.5">
          <span className="hidden sm:inline">Tools</span>
          <PanelRight className="size-4" />
        </Button>
      </div>

      {messages.length === 0 ? (
        <ChatEmptyState onQuickAction={handleSend} />
      ) : (
        <MessageList messages={messages} />
      )}

      <ChatInput
        onSend={handleSend}
        modelId={modelId}
        onModelChange={setModelId}
        disabled={sending}
      />
    </div>
  )
}
