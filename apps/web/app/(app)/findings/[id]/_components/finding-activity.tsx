import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { Finding } from "@/types"

function formatDate(date: Date) {
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export function FindingActivity({ finding }: { finding: Finding }) {
  const events: { date: Date; label: string }[] = [
    { date: finding.createdAt, label: "Finding discovered" },
  ]

  if (finding.status === "CONFIRMED") {
    events.push({ date: finding.updatedAt, label: "Confirmed by analyst" })
  }
  if (finding.status === "RESOLVED") {
    events.push({ date: finding.updatedAt, label: "Marked as resolved" })
  }
  if (finding.status === "FALSE_POSITIVE") {
    events.push({ date: finding.updatedAt, label: "Marked as false positive" })
  }
  if (
    finding.updatedAt.getTime() !== finding.createdAt.getTime() &&
    finding.status === "OPEN"
  ) {
    events.push({ date: finding.updatedAt, label: "Last updated" })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <ol className="relative border-l border-border ml-2">
          {events.map((e, i) => (
            <li key={i} className="mb-4 last:mb-0 ml-4">
              <div className="absolute -left-1.5 size-3 rounded-full border-2 border-background bg-primary" />
              <p className="text-sm font-medium">{e.label}</p>
              <time className="text-xs text-muted-foreground">
                {formatDate(e.date)}
              </time>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  )
}
