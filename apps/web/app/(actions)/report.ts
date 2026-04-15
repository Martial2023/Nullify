'use server'

import { getUser } from "@/lib/auth-session"
import { fastapiClient } from "@/lib/fastapi-client"
import prisma from "@/lib/prisma"
import type { Report } from "@/types"

export async function getReports(projectId: string): Promise<Report[]> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const project = await prisma.project.findFirst({
      where: { id: projectId, ownerId: user.id },
    })
    if (!project) throw new Error("Project not found")

    return prisma.report.findMany({
      where: { projectId },
      orderBy: { createdAt: "desc" },
    }) as Promise<Report[]>
  } catch (error) {
    console.log("Error while getting Reports: ", error)
    throw new Error("Error while getting Reports")
  }
}

export async function getReport(id: string): Promise<Report | null> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const report = await prisma.report.findFirst({
      where: {
        id,
        project: { ownerId: user.id },
      },
    })

    return report as Report | null
  } catch (error) {
    console.log("Error while getting Report: ", error)
    throw new Error("Error while getting Report")
  }
}

export async function generateReport(
  projectId: string,
  title: string
): Promise<Report> {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const project = await prisma.project.findFirst({
      where: { id: projectId, ownerId: user.id },
    })
    if (!project) throw new Error("Project not found")

    // Create report record as GENERATING
    const report = await prisma.report.create({
      data: {
        title,
        status: "GENERATING",
        projectId,
        createdBy: user.id,
      },
    })

    // Call FastAPI (mock for now)
    const result = await fastapiClient.generateReport(projectId)

    // Update report with generated content
    return prisma.report.update({
      where: { id: report.id },
      data: {
        status: "READY",
        summary: result.summary,
        content: result.content
          ? (JSON.parse(JSON.stringify(result.content)) as object)
          : undefined,
      },
    }) as unknown as Report
  } catch (error) {
    console.log("Error while generating repport")
    throw new Error("Error while generating report")
  }
}

export async function deleteReport(id: string) {
  try {
    const user = await getUser()
    if (!user) throw new Error("User not authenticated")

    const report = await prisma.report.findFirst({
      where: {
        id,
        project: { ownerId: user.id },
      },
    })
    if (!report) throw new Error("Report not found")

    await prisma.report.delete({ where: { id } })
  } catch (error) {
    console.log("Error while deleting report: ", error)
    throw new Error("Error while deleting report")
  }
}
