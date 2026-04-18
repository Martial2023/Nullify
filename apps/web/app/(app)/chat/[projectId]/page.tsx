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
import {
  startScan,
  updateScanStatus,
  persistFindings,
} from "@/app/(actions)/scan"
import { DEFAULT_MODEL_ID } from "@/lib/models"
import type { Message, ChatSession, Project, ToolCall } from "@/types"
import type { SSEEvent, ToolFinding } from "@/types/api"
import { MessageList } from "../_components/message-list"
import { ChatInput } from "../_components/chat-input"
import { ChatEmptyState } from "../_components/chat-empty-state"
import { ContextPanel } from "../_components/context-panel"
import { ToolsPanel } from "../_components/tools-panel"
import MinLoader from "@/components/MinLoader"
import { toast } from "sonner"

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
  const [liveFindings, setLiveFindings] = useState<ToolFinding[]>([])

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
      toast.error("Failed to load chat session")
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
    setLiveFindings([])

    try {
      await persistUserMessage(session.id, content)

      // 2. Build history from previous messages (exclude the optimistic user msg)
      const history = messages
        .filter((m) => m.role === "USER" || m.role === "ASSISTANT")
        .map((m) => ({
          role: m.role === "USER" ? "user" : "assistant",
          content: m.content,
        }))

      // 3. Stream from FastAPI via Next.js proxy
      const resp = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: content,
          session_id: session.id,
          project_id: project.id,
          model: modelId,
          history,
        }),
      })

      if (!resp.ok || !resp.body) {
        throw new Error(`Stream error: ${resp.status}`)
      }

      // 4. Create placeholder assistant message
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

      // 5. Read SSE stream
      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""
      let finalContent = ""
      let collectedToolCalls: ToolCall[] | undefined
      // Track scans created during this stream for persistence
      const scanIds = new Map<string, string>() // tool_call_id -> scanId

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
                setToolsOpen(true)

                // Persist scan in DB as RUNNING
                const target = (event.args?.target as string) ?? project.targets?.[0] ?? ""
                startScan(project.id, event.name, target, event.args ?? {})
                  .then((scan) => {
                    scanIds.set(event.tool_call_id!, scan.id)
                    updateScanStatus(scan.id, "RUNNING").catch(console.error)
                  })
                  .catch(console.error)
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
                if (event.findings && event.findings.length > 0) {
                  setLiveFindings((prev) => [...prev, ...event.findings!])

                  // Persist findings in DB
                  const scanId = scanIds.get(event.tool_call_id)
                  if (scanId) {
                    const dbFindings = event.findings.map((f) => ({
                      severity: f.severity ?? "INFO",
                      title: f.title ?? f.type ?? "Finding",
                      description: f.description ?? JSON.stringify(f),
                      target: f.subdomain ?? f.url ?? (f.port ? `port ${f.port}` : undefined),
                      evidence: f.service ?? undefined,
                    }))
                    persistFindings(scanId, dbFindings).catch(console.error)
                  }
                }

                // Mark scan as COMPLETED
                const completedScanId = scanIds.get(event.tool_call_id)
                if (completedScanId) {
                  updateScanStatus(
                    completedScanId,
                    "COMPLETED",
                    event.result ?? undefined
                  ).catch(console.error)
                }
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
              // Mark all in-progress scans as FAILED
              for (const scanId of scanIds.values()) {
                updateScanStatus(scanId, "FAILED", undefined, event.content ?? "Unknown error")
                  .catch(console.error)
              }
              break
          }
        }
      }

      // 6. Persist assistant message in DB
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
      toast.error("Failed to send message")
    } finally {
      setSending(false)
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
        liveFindings={liveFindings}
      />
    </div>
  )
}
