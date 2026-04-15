import { StatCard } from "@/components/StatCard"
import type { DashboardStats } from "@/app/(actions)/dashboard"
import { ListChecks, AlertTriangle, Server, ShieldCheck } from "lucide-react"

export function StatsGrid({ stats }: { stats: DashboardStats }) {
  return (
    <div className="grid grid-cols-1 gap-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card *:data-[slot=card]:shadow-xs @xl/main:grid-cols-2 @5xl/main:grid-cols-4 dark:*:data-[slot=card]:bg-card">
      <StatCard
        icon={ListChecks}
        label="Active Tasks"
        value={stats.activeTasks}
      />
      <StatCard
        icon={AlertTriangle}
        label="Open Findings"
        value={stats.openFindings}
      />
      <StatCard
        icon={Server}
        label="Assets Monitored"
        value={stats.assetsMonitored}
      />
      <StatCard
        icon={ShieldCheck}
        label="Compliance Score"
        value={`${stats.complianceScore}%`}
      />
    </div>
  )
}
