"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { PanelLeft, PanelRight } from "lucide-react"
import { createProject } from "@/app/(actions)/project"
import { createChatSession, sendMessage } from "@/app/(actions)/chat"
import { DEFAULT_MODEL_ID } from "@/lib/models"
import type { Message } from "@/types"
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
      // Create project + session + send message
      const project = await createProject({
        name: generateProjectName(content),
      })
      const session = await createChatSession(project.id, generateProjectName(content))
      const assistantMsg = await sendMessage(session.id, content, modelId)

      setMessages((prev) => [...prev, assistantMsg])

      // Redirect to the real chat page (replaces history)
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
