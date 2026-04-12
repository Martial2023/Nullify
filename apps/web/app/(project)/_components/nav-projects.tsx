"use client"

import { deleteProject, getProjectPreviews } from "@/app/(actions)/ations"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import ProjectPreview from "@/types"
import { MoreHorizontalIcon, FolderIcon, ShareIcon, Trash2Icon, Loader2 } from "lucide-react"
import Link from "next/link"
import { useState } from "react"
import { toast } from "sonner"
import DeleteProjectModal from "./DeleteProjectModal"

export function NavProjects({
  items,
}: {
  items: {
    name: string
    url: string
    icon: React.ReactNode
  }[]
}) {
  const { isMobile } = useSidebar()
  const [limit, setLimit] = useState<number>(5)
  const [projects, setProjects] = useState<ProjectPreview[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [deletingProjectIds, setDeletingProjectIds] = useState<string[]>([])

  const fetchProjects = async () => {
    try {
      setLoading(true)
      const projects = await getProjectPreviews()
      setProjects(projects)
    } catch (error) {
      console.error("Error fetching projects:", error)
      toast.error("Failed to load projects")
    } finally {
      setLoading(false)
    }
  }



  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>PROJECTS</SidebarGroupLabel>
      <SidebarMenu>
        {projects.slice(0, limit).map((item) => (
          <SidebarMenuItem key={item.name}>
            <SidebarMenuButton asChild>
              <Link href={`/chat/${item.id}`}>
                <FolderIcon />
                <span>{item.name}</span>
              </Link>
            </SidebarMenuButton>
            {
              deletingProjectIds.includes(item.id) ? (
                <Loader2 className="animate-spin" />
              ) : (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <SidebarMenuAction
                      showOnHover
                      className="rounded-sm data-[state=open]:bg-accent"
                    >
                      <MoreHorizontalIcon
                      />
                      <span className="sr-only">More</span>
                    </SidebarMenuAction>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent
                    className="w-24 rounded-lg"
                    side={isMobile ? "bottom" : "right"}
                    align={isMobile ? "end" : "start"}
                  >
                    <DropdownMenuItem>
                      <FolderIcon
                      />
                      <span>Open</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <ShareIcon
                      />
                      <span>Share</span>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DeleteProjectModal
                      deletingProjectIds={deletingProjectIds}
                      setProjects={setProjects}
                      setDeletingProjectIds={setDeletingProjectIds}
                      projectId={item.id}
                      projectName={item.name}
                    >
                      <DropdownMenuItem
                        variant="destructive"
                      >
                        <Trash2Icon
                        />
                        <span>Delete</span>
                      </DropdownMenuItem>
                    </DeleteProjectModal>
                  </DropdownMenuContent>
                </DropdownMenu>
              )
            }
          </SidebarMenuItem >
        ))}

        {
          limit < items.length && (
            <SidebarMenuItem>
              <SidebarMenuButton className="text-sidebar-foreground/70" onClick={() => setLimit(limit + 5)} >
                <MoreHorizontalIcon className="text-sidebar-foreground/70" />
                <span>More</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          )
        }
      </SidebarMenu >
    </SidebarGroup >
  )
}
