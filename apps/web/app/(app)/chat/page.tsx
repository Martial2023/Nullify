"use client"
import { getProjectPreviews } from "@/app/(actions)/project"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card"
import { EmptyState } from "@/components/EmptyState"
import { Crosshair, FolderOpen } from "lucide-react"
import Link from "next/link"
import { toast } from "sonner"
import { useEffect, useState } from "react"
import { ProjectPreview } from "@/types/project"
import MinLoader from "@/components/MinLoader"

export default function ChatIndexPage() {
  const [projects, setProjects] = useState<ProjectPreview[]>([])
  const [loading, setLoading] = useState<boolean>(true)

  const fetchProjects = async () => {
    try {
      setLoading(true)
      const data = await getProjectPreviews()
      setProjects(data)
    } catch (error) {
      toast.error("Failed to load projects. Please try again.")
    } finally {
      setLoading(false)
    }
  }
  useEffect(() => {
    fetchProjects()
  }, [])

  return (
    <main className="flex flex-col gap-4 p-4 lg:gap-6 lg:p-6">
      <h1 className="text-2xl font-bold tracking-tight">Chat</h1>
      <p className="text-sm text-muted-foreground">
        Select a project to start a security assessment chat.
      </p>

      {
        loading ? (
          <div className='flex flex-col items-center justify-center h-96'>
            <MinLoader />
            <p>Chargement...</p>
          </div>
        ) :
          projects.length === 0 ? (
            <EmptyState
              icon={FolderOpen}
              title="No projects yet"
              description="Create a project first to start chatting with the AI."
            />
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {projects.map((p) => (
                <Link key={p.id} href={`/chat/${p.id}`}>
                  <Card className="transition-colors hover:bg-muted/50">
                    <CardHeader>
                      <CardTitle>{p.name}</CardTitle>
                      <CardDescription className="flex items-center gap-1.5 pt-1 text-xs">
                        <Crosshair className="size-3" />
                        Last updated {new Date(p.updatedAt).toLocaleDateString()}
                      </CardDescription>
                    </CardHeader>
                  </Card>
                </Link>
              ))}
            </div>
          )}
    </main>
  )
}
