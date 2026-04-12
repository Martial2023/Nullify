'use server'
import { getUser } from "@/lib/auth-session"
import prisma from "@/lib/prisma"
import ProjectPreview from "@/types"


export async function getProjectPreviews(): Promise<ProjectPreview[]>{
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
        })
        return projects
    } catch (error) {
        console.error("Error fetching projects:", error)
        throw new Error("Failed to fetch projects")
    }
}

type deleteProjectParams = {
    id: string
}
export async function deleteProject({ id }: deleteProjectParams) {
    try {
        const user = await getUser()
        if (!user) {
            throw new Error("User not authenticated")
        }

        await prisma.project.deleteMany({
            where: {
                id,
                ownerId: user.id,
            },
        })
    } catch (error) {
        console.error("Error deleting project:", error)
        throw new Error("Failed to delete project")
    }
}