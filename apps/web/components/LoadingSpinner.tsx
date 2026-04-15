import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"

const sizes = {
  sm: "size-4",
  md: "size-6",
  lg: "size-8",
} as const

export function LoadingSpinner({
  size = "md",
  className,
}: {
  size?: keyof typeof sizes
  className?: string
}) {
  return (
    <Loader2
      className={cn("animate-spin text-muted-foreground", sizes[size], className)}
    />
  )
}
