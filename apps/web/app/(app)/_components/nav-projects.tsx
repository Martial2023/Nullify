"use client"

import { useEffect, useState } from "react"
import { usePathname } from "next/navigation"
import { deleteProject, getProjectPreviews } from "@/app/(actions)/project"
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
import type { ProjectPreview } from "@/types"
import { MoreHorizontalIcon, FolderIcon, ShareIcon, Trash2Icon, Loader } from "lucide-react"
import Link from "next/link"
import { toast } from "sonner"
import DeleteProjectModal from "./DeleteProjectModal"

export function NavProjects() {
  const { isMobile, setOpenMobile } = useSidebar()
  const pathname = usePathname()
  const [limit, setLimit] = useState(5)
  const [projects, setProjects] = useState<ProjectPreview[]>([])
  const [loading, setLoading] = useState(true)
  const [deletingProjectIds, setDeletingProjectIds] = useState<string[]>([])

  useEffect(() => {
    setLoading(true)
    getProjectPreviews()
      .then(setProjects)
      .catch(() => toast.error("Failed to load projects"))
      .finally(() => setLoading(false))
  }, [pathname])

  const handleNavClick = () => {
    if (isMobile) setOpenMobile(false)
  }

  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>PROJECTS</SidebarGroupLabel>
      <SidebarMenu>
        {loading && projects.length === 0 ? (
          <SidebarMenuItem>
            <SidebarMenuButton disabled>
              <Loader className="size-4 animate-spin" />
              <span>Loading...</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ) : (
          projects.slice(0, limit).map((item) => (
            <SidebarMenuItem key={item.id}>
              <SidebarMenuButton asChild isActive={pathname === `/chat/${item.id}`}>
                <Link href={`/chat/${item.id}`} onClick={handleNavClick}>
                  <FolderIcon />
                  <span>{item.name}</span>
                </Link>
              </SidebarMenuButton>
              {deletingProjectIds.includes(item.id) ? (
                <SidebarMenuButton>
                  <Loader className="size-4 animate-spin" />
                </SidebarMenuButton>
              ) : (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <SidebarMenuAction
                      showOnHover
                      className="rounded-sm data-[state=open]:bg-accent cursor-pointer"
                    >
                      <MoreHorizontalIcon />
                      <span className="sr-only">More</span>
                    </SidebarMenuAction>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent
                    className="w-24 rounded-lg"
                    side={isMobile ? "bottom" : "right"}
                    align={isMobile ? "end" : "start"}
                  >
                    <DropdownMenuItem asChild>
                      <Link href={`/chat/${item.id}`}>
                        <FolderIcon />
                        <span>Open</span>
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <ShareIcon />
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
                      <DropdownMenuItem variant="destructive">
                        <Trash2Icon />
                        <span>Delete</span>
                      </DropdownMenuItem>
                    </DeleteProjectModal>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </SidebarMenuItem>
          ))
        )}

        {projects.length > limit && (
          <SidebarMenuItem>
            <SidebarMenuButton
              className="text-sidebar-foreground/70"
              onClick={() => setLimit((l) => l + 5)}
            >
              <MoreHorizontalIcon className="text-sidebar-foreground/70" />
              <span>More</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        )}
      </SidebarMenu>
    </SidebarGroup>
  )
}
