'use server'

import { getUser } from "@/lib/auth-session"
import prisma from "@/lib/prisma"
import type { Finding, FindingStatus, Severity } from "@/types"

export async function getFindings(
  projectId: string,
  filters?: { severity?: Severity; status?: FindingStatus }
): Promise<Finding[]> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    // Verify project ownership
    const project = await prisma.project.findFirst({
      where: { id: projectId, ownerId: user.id },
    })
    if (!project) throw new Error("Project not found")

    return prisma.finding.findMany({
      where: {
        scan: { projectId },
        ...(filters?.severity && { severity: filters.severity }),
        ...(filters?.status && { status: filters.status }),
      },
      orderBy: { createdAt: "desc" },
    })
  } catch (error) {
    console.log("Error while getting Findings: ", error)
    throw new Error("Error while getting Findings")
  }
}

export async function getAllFindings(filters?: {
  severity?: Severity
  status?: FindingStatus
  search?: string
}): Promise<Finding[]> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    return prisma.finding.findMany({
      where: {
        scan: { project: { ownerId: user.id } },
        ...(filters?.severity && { severity: filters.severity }),
        ...(filters?.status && { status: filters.status }),
        ...(filters?.search && {
          title: { contains: filters.search, mode: "insensitive" as const },
        }),
      },
      orderBy: { createdAt: "desc" },
    })
  } catch (error) {
    console.log("Error while getting all Findings: ", error)
    throw new Error("Error while getting all Findings")
  }
}

export async function getFinding(id: string): Promise<Finding | null> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const finding = await prisma.finding.findFirst({
      where: {
        id,
        scan: { project: { ownerId: user.id } },
      },
    })

    return finding
  } catch (error) {
    console.log("Error while getting Finding: ", error)
    throw new Error("Error while getting Finding")
  }
}

export async function updateFindingStatus(
  id: string,
  status: FindingStatus
): Promise<Finding> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    // Verify ownership through scan → project chain
    const finding = await prisma.finding.findFirst({
      where: {
        id,
        scan: { project: { ownerId: user.id } },
      },
    })
    if (!finding) throw new Error("Finding not found")

    return prisma.finding.update({
      where: { id },
      data: { status },
    })
  } catch (error) {
    console.log("Error while updatding findings status", error)
    throw new Error("Error while updating findings status")
  }
}
