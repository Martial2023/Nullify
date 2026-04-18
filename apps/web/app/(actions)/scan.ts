'use server'

import { getUser } from "@/lib/auth-session"
import { fastapiClient } from "@/lib/fastapi-client"
import prisma from "@/lib/prisma"
import type { Scan, ScanWithFindings } from "@/types"

export async function getScans(projectId: string): Promise<Scan[]> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const project = await prisma.project.findFirst({
      where: { id: projectId, ownerId: user.id },
    })
    if (!project) throw new Error("Project not found")

    return prisma.scan.findMany({
      where: { projectId },
      orderBy: { startedAt: "desc" },
    }) as Promise<Scan[]>
  } catch (error) {
    console.log("Error while getting Scans: ", error)
    throw new Error("Error while getting Scans")
  }
}

export async function getScan(
  id: string
): Promise<ScanWithFindings | null> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const scan = await prisma.scan.findFirst({
      where: {
        id,
        project: { ownerId: user.id },
      },
      include: { findings: true },
    })

    if (!scan) return null

    return scan as unknown as ScanWithFindings
  } catch (error) {
    console.log("Error while getting Scan: ", error)
    throw new Error("Error while getting Scan")
  }
}

export async function startScan(
  projectId: string,
  tool: string,
  target: string,
  args: Record<string, unknown> = {}
): Promise<Scan> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const project = await prisma.project.findFirst({
      where: { id: projectId, ownerId: user.id },
    })
    if (!project) throw new Error("Project not found")

    // Create scan record as PENDING
    const scan = await prisma.scan.create({
      data: {
        tool,
        target,
        args: args as object,
        status: "PENDING",
        projectId,
        startedBy: user.id,
      },
    })

    fastapiClient.runScan(tool, target, args).catch(console.error)

    return scan as unknown as Scan
  } catch (error) {
    console.log("Error while starting scan: ", error)
    throw new Error("Error while starting scan")
  }
}

export async function updateScanStatus(
  scanId: string,
  status: "RUNNING" | "COMPLETED" | "FAILED",
  output?: string,
  error?: string
): Promise<void> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const scan = await prisma.scan.findFirst({
      where: { id: scanId, project: { ownerId: user.id } },
    })
    if (!scan) throw new Error("Scan not found")

    await prisma.scan.update({
      where: { id: scanId },
      data: {
        status,
        output: output ?? undefined,
        error: error ?? undefined,
        endedAt: status === "COMPLETED" || status === "FAILED" ? new Date() : undefined,
      },
    })
  } catch (error) {
    console.log("Error while updating scan status:", error)
    throw new Error("Error while updating scan status")
  }
}

export async function persistFindings(
  scanId: string,
  findings: {
    severity: string
    title: string
    description: string
    target?: string
    evidence?: string
    remediation?: string
  }[]
): Promise<void> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const scan = await prisma.scan.findFirst({
      where: { id: scanId, project: { ownerId: user.id } },
    })
    if (!scan) throw new Error("Scan not found")

    if (findings.length === 0) return

    await prisma.finding.createMany({
      data: findings.map((f) => ({
        scanId,
        severity: normalizeSeverity(f.severity),
        title: f.title,
        description: f.description,
        target: f.target ?? null,
        evidence: f.evidence ?? null,
        remediation: f.remediation ?? null,
      })),
    })
  } catch (error) {
    console.log("Error while persisting findings:", error)
    throw new Error("Error while persisting findings")
  }
}

function normalizeSeverity(
  raw: string
): "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO" {
  const upper = raw.toUpperCase()
  if (["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"].includes(upper)) {
    return upper as "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO"
  }
  return "INFO"
}

export async function cancelScan(id: string): Promise<Scan> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const scan = await prisma.scan.findFirst({
      where: {
        id,
        project: { ownerId: user.id },
        status: { in: ["PENDING", "RUNNING"] },
      },
    })
    if (!scan) throw new Error("Scan not found or cannot be cancelled")

    return prisma.scan.update({
      where: { id },
      data: { status: "CANCELLED", endedAt: new Date() },
    }) as unknown as Scan
  } catch (error) {
    console.log("Error while canceling scan: ", error)
    throw new Error("Error while canceling scan")
  }
}
