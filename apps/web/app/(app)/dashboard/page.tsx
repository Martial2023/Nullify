export const dynamic = "force-dynamic"

import { getDashboardStats } from "@/app/(actions)/dashboard"
import { StatsGrid } from "./_components/stats-grid"
import { SeverityChart } from "./_components/severity-chart"
import { TrendChart } from "./_components/trend-chart"
import { RecentFindingsTable } from "./_components/recent-findings-table"

export default async function DashboardPage() {
  const stats = await getDashboardStats()

  return (
    <main className="@container/main flex flex-col gap-4 p-4 lg:gap-6 lg:p-6">
      <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
      <StatsGrid stats={stats} />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <SeverityChart distribution={stats.severityDistribution} />
        <TrendChart data={stats.weeklyTrend} />
      </div>
      <RecentFindingsTable findings={stats.recentFindings} />
    </main>
  )
}
