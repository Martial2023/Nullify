import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

type StatusVariant = "scan" | "finding" | "report"

const colorMap: Record<StatusVariant, Record<string, string>> = {
  scan: {
    PENDING: "bg-zinc-500",
    RUNNING: "bg-blue-500",
    COMPLETED: "bg-emerald-500",
    FAILED: "bg-red-500",
    CANCELLED: "bg-zinc-400",
  },
  finding: {
    OPEN: "bg-red-500",
    CONFIRMED: "bg-orange-500",
    FALSE_POSITIVE: "bg-zinc-400",
    RESOLVED: "bg-emerald-500",
  },
  report: {
    GENERATING: "bg-blue-500",
    READY: "bg-emerald-500",
    FAILED: "bg-red-500",
  },
}

const labelMap: Record<string, string> = {
  PENDING: "Pending",
  RUNNING: "Running",
  COMPLETED: "Completed",
  FAILED: "Failed",
  CANCELLED: "Cancelled",
  OPEN: "Open",
  CONFIRMED: "Confirmed",
  FALSE_POSITIVE: "False Positive",
  RESOLVED: "Resolved",
  GENERATING: "Generating",
  READY: "Ready",
}

export function StatusBadge({
  status,
  variant = "finding",
  className,
}: {
  status: string
  variant?: StatusVariant
  className?: string
}) {
  const dotColor = colorMap[variant]?.[status] ?? "bg-zinc-400"
  const label = labelMap[status] ?? status

  return (
    <Badge
      variant="outline"
      className={cn("gap-1.5 font-normal", className)}
    >
      <span className={cn("size-2 rounded-full", dotColor)} />
      {label}
    </Badge>
  )
}
