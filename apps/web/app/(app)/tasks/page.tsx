import { EmptyState } from "@/components/EmptyState"
import { ListChecks } from "lucide-react"

export default function TasksPage() {
  return (
    <main className="flex flex-col gap-4 p-4 lg:gap-6 lg:p-6">
      <h1 className="text-2xl font-bold tracking-tight">Tasks</h1>
      <EmptyState
        icon={ListChecks}
        title="No tasks yet"
        description="Tasks will appear here when scans are running."
      />
    </main>
  )
}
