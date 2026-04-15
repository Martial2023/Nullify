"use client"

import { NavProjects } from "@/app/(app)/_components/nav-projects"
import { NavMain } from "@/app/(app)/_components/nav-main"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import {
  LayoutDashboardIcon,
  FileChartColumnIcon,
  Code,
  MessageCircle,
  AlertTriangle,
  Server,
  ListChecks,
} from "lucide-react"
import { NavUser } from "./nav-user"
import Link from "next/link"

const navMain = [
  { title: "Dashboard", url: "/dashboard", icon: <LayoutDashboardIcon /> },
  { title: "Chat", url: "/chat", icon: <MessageCircle /> },
  { title: "Tasks", url: "/tasks", icon: <ListChecks /> },
  { title: "Findings", url: "/findings", icon: <AlertTriangle /> },
  { title: "Assets", url: "/assets", icon: <Server /> },
  { title: "Reports", url: "/reports", icon: <FileChartColumnIcon /> },
]

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/dashboard">
                <Code />
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <h2 className="text-xl font-bold">
                    <span className="text-primary">Nullify</span>
                  </h2>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navMain} />
        <NavProjects />
      </SidebarContent>
      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
    </Sidebar>
  )
}
