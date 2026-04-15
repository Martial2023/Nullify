"use client"

import { useEffect, useRef } from "react"
import type { Message } from "@/types"
import { Bot } from "lucide-react"
import { cn } from "@/lib/utils"
import { MarkdownRenderer } from "@/components/MarkdownRenderer"
import { ThinkingIndicator } from "@/components/ThinkingIndicator"

function UserMessage({ message }: { message: Message }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[75%] rounded-2xl rounded-br-sm bg-primary px-4 py-2.5 text-primary-foreground">
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  )
}

function AssistantMessage({ message }: { message: Message }) {
  return (
    <div className="flex gap-3">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted">
        <Bot className="size-4" />
      </div>
      <div className="max-w-[75%] space-y-2">
        <div className="rounded-2xl rounded-tl-sm bg-muted px-4 py-2.5">
          <MarkdownRenderer content={message.content} />
        </div>
        {message.toolCalls?.map((tc) => (
          <div
            key={tc.id}
            className="rounded-lg border bg-zinc-950 p-3 font-mono text-xs text-zinc-300"
          >
            <span className="text-emerald-400">$ {tc.name}</span>{" "}
            <span className="text-zinc-500">
              {JSON.stringify(tc.args)}
            </span>
            {tc.result && (
              <pre className="mt-1 max-h-48 overflow-y-auto text-zinc-400 whitespace-pre-wrap">
                {tc.result}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function ToolMessage({ message }: { message: Message }) {
  return (
    <div className="flex gap-3 pl-11">
      <div className="w-full max-w-[75%] rounded-lg border bg-zinc-950 p-3 font-mono text-xs text-zinc-300">
        <pre className="whitespace-pre-wrap">{message.content}</pre>
      </div>
    </div>
  )
}

const componentMap = {
  USER: UserMessage,
  ASSISTANT: AssistantMessage,
  TOOL: ToolMessage,
} as const

export function MessageList({
  messages,
  isThinking = false,
  className,
}: {
  messages: Message[]
  isThinking?: boolean
  className?: string
}) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages.length, isThinking])

  return (
    <div className={cn("flex-1 overflow-y-auto p-4", className)}>
      <div className="mx-auto flex max-w-3xl flex-col gap-4">
        {messages.map((m) => {
          const Component = componentMap[m.role]
          return <Component key={m.id} message={m} />
        })}
        {isThinking && <ThinkingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
