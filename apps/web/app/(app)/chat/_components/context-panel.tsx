"use client"

import { useEffect, useState } from "react"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { getProject } from "@/app/(actions)/project"
import type { Project } from "@/types"
import { FolderOpen, Crosshair, Brain } from "lucide-react"

const preventClose = (e: Event) => e.preventDefault()

export function ContextPanel({
  projectId,
  open,
  onOpenChange,
}: {
  projectId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const [project, setProject] = useState<Project | null>(null)

  useEffect(() => {
    if (open && !project) {
      getProject(projectId).then(setProject).catch(console.error)
    }
  }, [open, project, projectId])

  return (
    <Sheet open={open} onOpenChange={onOpenChange} modal={false}>
      <SheetContent
        side="left"
        overlay={false}
        onInteractOutside={preventClose}
        onPointerDownOutside={preventClose}
        className="left-0 md:left-[var(--sidebar-width)]"
      >
        <SheetHeader>
          <SheetTitle>Context</SheetTitle>
        </SheetHeader>

        <div className="flex flex-col gap-5 overflow-y-auto px-4 pb-4">
          <section className="space-y-2">
            <h3 className="flex items-center gap-1.5 text-xs font-medium uppercase text-muted-foreground">
              <FolderOpen className="size-3.5" />
              Project
            </h3>
            {project ? (
              <div className="space-y-1">
                <p className="font-medium">{project.name}</p>
                {project.description && (
                  <p className="text-xs text-muted-foreground">
                    {project.description}
                  </p>
                )}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">Loading...</p>
            )}
          </section>

          <Separator />

          <section className="space-y-2">
            <h3 className="flex items-center gap-1.5 text-xs font-medium uppercase text-muted-foreground">
              <Crosshair className="size-3.5" />
              Targets
            </h3>
            {project?.targets.length ? (
              <div className="flex flex-wrap gap-1.5">
                {project.targets.map((t) => (
                  <Badge key={t} variant="secondary" className="font-mono text-xs">
                    {t}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No targets defined</p>
            )}
          </section>

          <Separator />

          <section className="space-y-2">
            <h3 className="flex items-center gap-1.5 text-xs font-medium uppercase text-muted-foreground">
              <Brain className="size-3.5" />
              Memory
            </h3>
            <p className="text-xs text-muted-foreground">
              No memory entries yet. The AI will remember context as you interact.
            </p>
          </section>
        </div>
      </SheetContent>
    </Sheet>
  )
}
