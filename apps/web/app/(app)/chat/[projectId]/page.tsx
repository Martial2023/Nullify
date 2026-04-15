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
  sendMessage,
} from "@/app/(actions)/chat"
import { DEFAULT_MODEL_ID } from "@/lib/models"
import type { Message, ChatSession, Project } from "@/types"
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
    if (!session) return

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

    try {
      const assistantMsg = await sendMessage(session.id, content, modelId)
      setMessages((prev) => [...prev, assistantMsg])
    } catch (error) {
      console.error("Failed to send message:", error)
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
      />
    </div>
  )
}
