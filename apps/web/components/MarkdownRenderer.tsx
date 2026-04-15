"use client"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeHighlight from "rehype-highlight"
import { cn } from "@/lib/utils"

export function MarkdownRenderer({
  content,
  className,
}: {
  content: string
  className?: string
}) {
  return (
    <div
      className={cn(
        "prose prose-sm dark:prose-invert max-w-none",
        // Headings
        "prose-headings:mb-2 prose-headings:mt-4 prose-headings:font-semibold",
        // Paragraphs
        "prose-p:my-1.5 prose-p:leading-relaxed",
        // Lists
        "prose-ul:my-1.5 prose-ol:my-1.5 prose-li:my-0.5",
        // Code
        "prose-code:rounded prose-code:bg-muted prose-code:px-1.5 prose-code:py-0.5 prose-code:text-xs prose-code:font-mono prose-code:before:content-none prose-code:after:content-none",
        "prose-pre:my-2 prose-pre:rounded-lg prose-pre:bg-zinc-950 prose-pre:p-3",
        // Tables
        "prose-table:my-2 prose-th:border prose-th:border-border prose-th:px-3 prose-th:py-1.5 prose-td:border prose-td:border-border prose-td:px-3 prose-td:py-1.5",
        // Links
        "prose-a:text-primary prose-a:underline-offset-2",
        // Strong
        "prose-strong:font-semibold",
        className
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
        {content}
      </ReactMarkdown>
    </div>
  )
}
