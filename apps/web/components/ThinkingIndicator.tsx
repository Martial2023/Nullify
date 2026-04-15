"use client"

import { Bot } from "lucide-react"

export function ThinkingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted">
        <Bot className="size-4" />
      </div>
      <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm bg-muted px-4 py-3">
        <div className="flex items-center gap-1">
          <span
            className="size-1.5 animate-bounce rounded-full bg-foreground/50"
            style={{ animationDelay: "0ms" }}
          />
          <span
            className="size-1.5 animate-bounce rounded-full bg-foreground/50"
            style={{ animationDelay: "150ms" }}
          />
          <span
            className="size-1.5 animate-bounce rounded-full bg-foreground/50"
            style={{ animationDelay: "300ms" }}
          />
        </div>
        <span className="text-xs text-muted-foreground">
          Nullify analyse...
        </span>
      </div>
    </div>
  )
}
