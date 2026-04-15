'use server'
import { getUser } from "@/lib/auth-session"
import prisma from "@/lib/prisma"
import type { Project, ProjectPreview } from "@/types"


export async function getProjectPreviews(): Promise<ProjectPreview[]> {
    try {
        const user = await getUser()
        if (!user) {
            throw new Error("User not authenticated")
        }
        const projects = await prisma.project.findMany({
            where: {
                ownerId: user.id,
            },
            select: {
                id: true,
                name: true,
                updatedAt: true,
            },
            orderBy: { updatedAt: "desc" },
        })
        return projects
    } catch (error) {
        console.error("Error fetching projects:", error)
        throw new Error("Failed to fetch projects")
    }
}

export async function getProject(id: string): Promise<Project | null> {
    try {
        const user = await getUser()
        if (!user) throw new Error("User not authenticated")

        return prisma.project.findFirst({
            where: { id, ownerId: user.id },
        })
    } catch (error) {
        console.log("Error fetching project:", error)
        throw new Error("Failed to fetch project")
    }
}

export async function createProject(data: {
    name: string
    description?: string
    targets?: string[]
}): Promise<Project> {
    try {
        const user = await getUser()
        if (!user) throw new Error("User not authenticated")

        return prisma.project.create({
            data: {
                name: data.name,
                description: data.description ?? null,
                targets: data.targets ?? [],
                ownerId: user.id,
            },
        })
    } catch (error) {
        console.error("Error creating project:", error)
        throw new Error("Failed to create project")
    }
}

export async function updateProject(
    id: string,
    data: Partial<Pick<Project, "name" | "description" | "targets">>
): Promise<Project> {
    try {
        const user = await getUser()
        if (!user) throw new Error("User not authenticated")

        const project = await prisma.project.findFirst({
            where: { id, ownerId: user.id },
        })
        if (!project) throw new Error("Project not found")

        return prisma.project.update({
            where: { id },
            data,
        })
    } catch(error){
        console.error("Error updating project:", error)
        throw new Error("Failed to update project")
    }
}

export async function deleteProject({ id }: { id: string }) { 
    try {
        const user = await getUser()
        if (!user) throw new Error("User not authenticated")

        await prisma.project.deleteMany({
            where: { id, ownerId: user.id },
        })
    } catch(error) {
        console.error("Error deleting project:", error)
        throw new Error("Failed to delete project")
    }
}