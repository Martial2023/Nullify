import { Button } from "@/components/ui/button"
import { Code } from "lucide-react"

const suggestions = [
  "Scan for vulnerabilities",
  "Enumerate subdomains",
  "Check open ports",
  "Analyze API security",
]

export function ChatEmptyState({
  onQuickAction,
}: {
  onQuickAction: (text: string) => void
}) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 p-8 text-center">
      <div className="flex size-16 items-center justify-center rounded-full bg-muted">
        <Code className="size-8 text-muted-foreground" />
      </div>
      <div className="space-y-2">
        <h2 className="text-xl font-semibold">Start a security assessment</h2>
        <p className="text-sm text-muted-foreground">
          Describe what you want to test and the AI will orchestrate the right tools.
        </p>
      </div>
      <div className="flex flex-wrap justify-center gap-2">
        {suggestions.map((s) => (
          <Button
            key={s}
            variant="outline"
            size="sm"
            onClick={() => onQuickAction(s)}
          >
            {s}
          </Button>
        ))}
      </div>
    </div>
  )
}
