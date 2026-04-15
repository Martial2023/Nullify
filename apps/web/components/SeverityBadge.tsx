import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import {
  ShieldAlert,
  ShieldX,
  ShieldEllipsis,
  Shield,
  Info,
} from "lucide-react"
import type { Severity } from "@/types"

const config: Record<
  Severity,
  { icon: React.ElementType; classes: string }
> = {
  CRITICAL: {
    icon: ShieldX,
    classes: "bg-red-500/15 text-red-700 dark:text-red-400",
  },
  HIGH: {
    icon: ShieldAlert,
    classes: "bg-orange-500/15 text-orange-700 dark:text-orange-400",
  },
  MEDIUM: {
    icon: ShieldEllipsis,
    classes: "bg-yellow-500/15 text-yellow-700 dark:text-yellow-400",
  },
  LOW: {
    icon: Shield,
    classes: "bg-blue-500/15 text-blue-700 dark:text-blue-400",
  },
  INFO: {
    icon: Info,
    classes: "bg-zinc-500/15 text-zinc-700 dark:text-zinc-400",
  },
}

const labels: Record<Severity, string> = {
  CRITICAL: "Critical",
  HIGH: "High",
  MEDIUM: "Medium",
  LOW: "Low",
  INFO: "Info",
}

export function SeverityBadge({
  severity,
  className,
}: {
  severity: Severity
  className?: string
}) {
  const { icon: Icon, classes } = config[severity]

  return (
    <Badge
      variant="secondary"
      className={cn(
        "gap-1 border-transparent font-medium",
        classes,
        className
      )}
    >
      <Icon className="size-3" />
      {labels[severity]}
    </Badge>
  )
}
