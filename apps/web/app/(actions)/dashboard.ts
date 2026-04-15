'use server'

import { getUser } from "@/lib/auth-session"
import prisma from "@/lib/prisma"
import type { Severity } from "@/types"

export interface WeeklyTrendItem {
  week: string
  findings: number
}

export interface DashboardStats {
  activeTasks: number
  openFindings: number
  assetsMonitored: number
  complianceScore: number
  severityDistribution: Record<string, number>
  weeklyTrend: WeeklyTrendItem[]
  recentFindings: {
    id: string
    severity: Severity
    status: string
    title: string
    target: string | null
    createdAt: Date
  }[]
}

export async function getDashboardStats(): Promise<DashboardStats> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const userFilter = { project: { ownerId: user.id } }

    // Weekly trend: findings created in the last 4 weeks
    const fourWeeksAgo = new Date()
    fourWeeksAgo.setDate(fourWeeksAgo.getDate() - 28)

    const [activeTasks, openFindings, projects, severityCounts, recentFindings, trendFindings] =
      await Promise.all([
        prisma.scan.count({
          where: { ...userFilter, status: { in: ["PENDING", "RUNNING"] } },
        }),
        prisma.finding.count({
          where: { scan: userFilter, status: { in: ["OPEN", "CONFIRMED"] } },
        }),
        prisma.project.findMany({
          where: { ownerId: user.id },
          select: { targets: true },
        }),
        prisma.finding.groupBy({
          by: ["severity"],
          where: { scan: userFilter },
          _count: true,
        }),
        prisma.finding.findMany({
          where: { scan: userFilter },
          orderBy: { createdAt: "desc" },
          take: 5,
          select: {
            id: true,
            severity: true,
            status: true,
            title: true,
            target: true,
            createdAt: true,
          },
        }),
        prisma.finding.findMany({
          where: {
            scan: userFilter,
            createdAt: { gte: fourWeeksAgo },
          },
          select: { createdAt: true },
        }),
      ])

    const totalTargets = projects.reduce((sum, p) => sum + p.targets.length, 0)
    const totalFindings = severityCounts.reduce((sum, s) => sum + s._count, 0)
    const criticalAndHigh = severityCounts
      .filter((s) => s.severity === "CRITICAL" || s.severity === "HIGH")
      .reduce((sum, s) => sum + s._count, 0)
    const complianceScore =
      totalFindings > 0
        ? Math.round(((totalFindings - criticalAndHigh) / totalFindings) * 100)
        : 100

    const severityDistribution: Record<string, number> = {
      CRITICAL: 0,
      HIGH: 0,
      MEDIUM: 0,
      LOW: 0,
      INFO: 0,
    }
    for (const s of severityCounts) {
      severityDistribution[s.severity] = s._count
    }

    // Build weekly trend from real data
    const weeklyTrend: WeeklyTrendItem[] = Array.from({ length: 4 }, (_, i) => {
      const weekStart = new Date()
      weekStart.setDate(weekStart.getDate() - (3 - i) * 7 - 7)
      const weekEnd = new Date()
      weekEnd.setDate(weekEnd.getDate() - (3 - i) * 7)
      const count = trendFindings.filter(
        (f) => f.createdAt >= weekStart && f.createdAt < weekEnd
      ).length
      return { week: `W${i + 1}`, findings: count }
    })

    return {
      activeTasks,
      openFindings,
      assetsMonitored: totalTargets,
      complianceScore,
      severityDistribution,
      weeklyTrend,
      recentFindings,
    }
  } catch (error) {
    console.error("Error fetching dashboard stats:", error)
    throw new Error("Failed to fetch dashboard stats")
  }
}
