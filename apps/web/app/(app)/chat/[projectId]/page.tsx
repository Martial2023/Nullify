"use client"
import { useState, useEffect, useCallback } from "react"
import { useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { LoadingSpinner } from "@/components/LoadingSpinner"
import { PanelLeft, PanelRight } from "lucide-react"
import { getProject } from "@/app/(actions)/project"
import {
  getChatSessions,
  createChatSession,
  getChatSession,
  persistUserMessage,
  persistAssistantMessage,
} from "@/app/(actions)/chat"
import { DEFAULT_MODEL_ID } from "@/lib/models"
import type { Message, ChatSession, Project, ToolCall } from "@/types"
import type { SSEEvent } from "@/types/api"
import { MessageList } from "../_components/message-list"
import { ChatInput } from "../_components/chat-input"
import { ChatEmptyState } from "../_components/chat-empty-state"
import { ContextPanel } from "../_components/context-panel"
import { ToolsPanel } from "../_components/tools-panel"
import MinLoader from "@/components/MinLoader"

export default function ChatPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [session, setSession] = useState<ChatSession | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [modelId, setModelId] = useState(DEFAULT_MODEL_ID)
  const [contextOpen, setContextOpen] = useState<boolean>(false)
  const [toolsOpen, setToolsOpen] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(true)
  const [sending, setSending] = useState<boolean>(false)
  const [liveToolCalls, setLiveToolCalls] = useState<ToolCall[]>([])

  const init = useCallback(async () => {
    try {
      setLoading(true)
      const proj = await getProject(projectId)
      setProject(proj)

      const sessions = await getChatSessions(projectId)
      let activeSession = sessions[0] ?? null

      if (!activeSession) {
        activeSession = await createChatSession(projectId, "New Chat")
      }

      setSession(activeSession)

      const full = await getChatSession(activeSession.id)
      setMessages(full?.messages ?? [])
    } catch (error) {
      console.error("Failed to init chat:", error)
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    init()
  }, [init])

  const handleSend = async (content: string) => {
    if (!session || !project) return

    // Optimistic: show user message immediately
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "USER",
      content,
      toolCalls: null,
      sessionId: session.id,
      createdAt: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])
    setSending(true)
    setLiveToolCalls([])

    try {
      // 1. Persist user message in DB
      await persistUserMessage(session.id, content)

      // 2. Stream from FastAPI via Next.js proxy
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

      // 3. Create placeholder assistant message
      const assistantId = crypto.randomUUID()
      const assistantMsg: Message = {
        id: assistantId,
        role: "ASSISTANT",
        content: "",
        toolCalls: null,
        sessionId: session.id,
        createdAt: new Date(),
      }
      setMessages((prev) => [...prev, assistantMsg])

      // 4. Read SSE stream
      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""
      let finalContent = ""
      let collectedToolCalls: ToolCall[] | undefined

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

          switch (event.event) {
            case "thinking":
              // Show LLM reasoning as streaming content
              if (event.content) {
                finalContent += event.content
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId ? { ...m, content: finalContent } : m
                  )
                )
              }
              break

            case "tool_start":
              if (event.tool_call_id && event.name) {
                const tc: ToolCall = {
                  id: event.tool_call_id,
                  name: event.name,
                  args: event.args ?? {},
                }
                setLiveToolCalls((prev) => [...prev, tc])
              }
              break

            case "tool_output":
              if (event.tool_call_id) {
                setLiveToolCalls((prev) =>
                  prev.map((tc) =>
                    tc.id === event.tool_call_id
                      ? { ...tc, result: event.result ?? "" }
                      : tc
                  )
                )
              }
              break

            case "message":
              finalContent = event.content ?? ""
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, content: finalContent } : m
                )
              )
              break

            case "done":
              collectedToolCalls = event.tool_calls ?? undefined
              break

            case "error":
              finalContent = `Error: ${event.content ?? "Unknown error"}`
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, content: finalContent } : m
                )
              )
              break
          }
        }
      }

      // 5. Persist assistant message in DB
      const saved = await persistAssistantMessage(
        session.id,
        finalContent,
        collectedToolCalls
      )

      // Update with DB id and final tool calls
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...saved }
            : m
        )
      )
    } catch (error) {
      console.error("Failed to send message:", error)
    } finally {
      setSending(false)
      setLiveToolCalls([])
    }
  }

  if (loading) {
    return (
      <div className="flex h-[calc(100vh-3rem)] items-center justify-center">
        <div className='flex flex-col items-center justify-center h-96'>
          <MinLoader />
          <p className="text-sm text-muted-foreground">
            Chargement...
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-3rem)] flex-col">
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b px-4 py-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setContextOpen((o) => !o)}
          className="gap-1.5"
        >
          <PanelLeft className="size-4" />
          <span className="hidden sm:inline">Context</span>
        </Button>
        <span className="text-sm font-medium truncate max-w-64">
          {session?.title ?? project?.name ?? "Chat"}
        </span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setToolsOpen((o) => !o)}
          className="gap-1.5"
        >
          <span className="hidden sm:inline">Tools</span>
          <PanelRight className="size-4" />
        </Button>
      </div>

      {/* Messages / Empty State */}
      {messages.length === 0 ? (
        <ChatEmptyState onQuickAction={handleSend} />
      ) : (
        <MessageList messages={messages} isThinking={sending} />
      )}

      {/* Input */}
      <ChatInput
        onSend={handleSend}
        modelId={modelId}
        onModelChange={setModelId}
        disabled={sending}
      />

      {/* Side Panels */}
      <ContextPanel
        projectId={projectId}
        open={contextOpen}
        onOpenChange={setContextOpen}
      />
      <ToolsPanel
        projectId={projectId}
        open={toolsOpen}
        onOpenChange={setToolsOpen}
        liveToolCalls={liveToolCalls}
      />
    </div>
  )
}
