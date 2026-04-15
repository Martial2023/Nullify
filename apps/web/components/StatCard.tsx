import {
  Card,
  CardAction,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUpIcon, TrendingDownIcon } from "lucide-react"
import { cn } from "@/lib/utils"
import type { LucideIcon } from "lucide-react"

export function StatCard({
  icon: Icon,
  label,
  value,
  delta,
  className,
}: {
  icon: LucideIcon
  label: string
  value: string | number
  delta?: { value: number; trend: "up" | "down" }
  className?: string
}) {
  return (
    <Card className={cn("@container/card", className)}>
      <CardHeader>
        <CardDescription className="flex items-center gap-1.5">
          <Icon className="size-4" />
          {label}
        </CardDescription>
        <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
          {value}
        </CardTitle>
        {delta && (
          <CardAction>
            <Badge variant="outline">
              {delta.trend === "up" ? (
                <TrendingUpIcon className="text-emerald-500" />
              ) : (
                <TrendingDownIcon className="text-red-500" />
              )}
              {delta.trend === "up" ? "+" : ""}
              {delta.value}%
            </Badge>
          </CardAction>
        )}
      </CardHeader>
    </Card>
  )
}
