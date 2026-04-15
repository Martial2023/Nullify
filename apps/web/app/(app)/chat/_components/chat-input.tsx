"use client"

import { useState, type KeyboardEvent } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { ModelSelector } from "@/components/ModelSelector"
import {
  ArrowUp,
  Ban,
  Bot,
  Clock,
  Mic,
  Paperclip,
  SlidersHorizontal,
  Sparkles,
} from "lucide-react"

export function ChatInput({
  onSend,
  modelId,
  onModelChange,
  disabled,
}: {
  onSend: (content: string) => void
  modelId: string
  onModelChange: (id: string) => void
  disabled?: boolean
}) {
  const [value, setValue] = useState("")

  const submit = () => {
    const trimmed = value.trim()
    if (!trimmed) return
    onSend(trimmed)
    setValue("")
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  const canSend = !disabled && value.trim().length > 0

  return (
    <div className="bg-background p-3">
      <div className="mx-auto max-w-3xl rounded-2xl border border-border/60 bg-card/40 px-3 pt-3 pb-2 shadow-sm backdrop-blur">
        <Textarea
          placeholder="Can you review the spec and..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          className="min-h-10 max-h-40 resize-none border-0 bg-transparent px-1 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0"
          rows={1}
        />

        <div className="mt-2 flex items-center justify-between gap-2">
          <div className="flex items-center gap-1">
            <Button
              type="button"
              size="icon"
              variant="ghost"
              className="size-8 rounded-full text-muted-foreground"
              aria-label="Attach file"
            >
              <Paperclip className="size-4" />
            </Button>

            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-8 gap-1.5 rounded-full px-3 text-xs"
            >
              <Bot className="size-3.5" />
              Agent
            </Button>

            <Button
              type="button"
              size="icon"
              variant="ghost"
              className="size-8 rounded-full text-muted-foreground"
              aria-label="Suggestions"
            >
              <Sparkles className="size-4" />
            </Button>

            <Button
              type="button"
              size="icon"
              variant="ghost"
              className="size-8 rounded-full text-muted-foreground"
              aria-label="Options"
            >
              <SlidersHorizontal className="size-4" />
            </Button>

            <div className="flex items-center gap-1.5 rounded-full border border-border/60 pl-2 pr-1 text-xs text-muted-foreground">
              <span className="hidden md:inline">Select agent</span>
              <ModelSelector value={modelId} onValueChange={onModelChange} />
            </div>

            <Button
              type="button"
              size="icon"
              variant="ghost"
              className="size-8 rounded-full text-muted-foreground/60"
              aria-label="Disabled tool"
              disabled
            >
              <Ban className="size-4" />
            </Button>

            <Button
              type="button"
              size="icon"
              variant="ghost"
              className="size-8 rounded-full text-muted-foreground"
              aria-label="History"
            >
              <Clock className="size-4" />
            </Button>
          </div>

          <div className="flex items-center gap-1">
            <Button
              type="button"
              size="icon"
              variant="ghost"
              className="size-8 rounded-full text-muted-foreground"
              aria-label="Voice input"
            >
              <Mic className="size-4" />
            </Button>
            <Button
              type="button"
              size="icon"
              onClick={submit}
              disabled={!canSend}
              className="size-8 rounded-full"
              aria-label="Send"
            >
              <ArrowUp className="size-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
