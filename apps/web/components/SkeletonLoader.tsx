import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

type Variant = "card" | "table-row" | "chat-message" | "list-item"

function CardSkeleton() {
  return (
    <div className="space-y-3 rounded-lg border p-4">
      <Skeleton className="h-5 w-2/5" />
      <Skeleton className="h-4 w-4/5" />
      <Skeleton className="h-4 w-3/5" />
    </div>
  )
}

function TableRowSkeleton() {
  return (
    <div className="flex items-center gap-4 py-3">
      <Skeleton className="h-4 w-8" />
      <Skeleton className="h-4 w-16" />
      <Skeleton className="h-4 flex-1" />
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-4 w-16" />
    </div>
  )
}

function ChatMessageSkeleton() {
  return (
    <div className="flex items-start gap-3">
      <Skeleton className="size-8 rounded-full" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
      </div>
    </div>
  )
}

function ListItemSkeleton() {
  return (
    <div className="flex items-center gap-3 py-2">
      <Skeleton className="size-6 rounded" />
      <div className="flex-1 space-y-1.5">
        <Skeleton className="h-4 w-2/3" />
        <Skeleton className="h-3 w-1/3" />
      </div>
    </div>
  )
}

const variants: Record<Variant, React.FC> = {
  card: CardSkeleton,
  "table-row": TableRowSkeleton,
  "chat-message": ChatMessageSkeleton,
  "list-item": ListItemSkeleton,
}

export function SkeletonLoader({
  variant,
  count = 1,
  className,
}: {
  variant: Variant
  count?: number
  className?: string
}) {
  const Component = variants[variant]

  return (
    <div className={cn("space-y-3", className)}>
      {Array.from({ length: count }, (_, i) => (
        <Component key={i} />
      ))}
    </div>
  )
}
