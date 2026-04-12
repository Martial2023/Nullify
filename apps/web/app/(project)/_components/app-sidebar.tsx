"use client"

import * as React from "react"

import { NavProjects } from "@/app/(project)/_components/nav-projects"
import { NavMain } from "@/app/(project)/_components/nav-main"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import { LayoutDashboardIcon, ListIcon, ChartBarIcon, FolderIcon, UsersIcon, CameraIcon, FileTextIcon, Settings2Icon, CircleHelpIcon, SearchIcon, DatabaseIcon, FileChartColumnIcon, FileIcon, CommandIcon, Code, MessageCircle, AlertTriangle, Server, CheckLine } from "lucide-react"
import { NavUser } from "./nav-user"
import Link from "next/link"

const data = {
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: (
        <LayoutDashboardIcon />
      ),
    },
    {
      title: "Chat",
      url: "/chat",
      icon: (
        <MessageCircle />
      ),
    },
    {
      title: "Tasks",
      url: "/tasks",
      icon: (
        <CheckLine />
      ),
    },
    {
      title: "Findings",
      url: "/findings",
      icon: (
        <AlertTriangle />
      ),
    },
    {
      title: "Assets",
      url: "/assets",
      icon: (
        <Server />
      ),
    },
    {
      title: "Reports",
      url: "/reports",
      icon: (
        <FileChartColumnIcon />
      ),
    },
  ],
  navClouds: [
    {
      title: "Capture",
      icon: (
        <CameraIcon
        />
      ),
      isActive: true,
      url: "#",
      items: [
        {
          title: "Active Proposals",
          url: "#",
        },
        {
          title: "Archived",
          url: "#",
        },
      ],
    },
    {
      title: "Proposal",
      icon: (
        <FileTextIcon
        />
      ),
      url: "#",
      items: [
        {
          title: "Active Proposals",
          url: "#",
        },
        {
          title: "Archived",
          url: "#",
        },
      ],
    },
    {
      title: "Prompts",
      icon: (
        <FileTextIcon
        />
      ),
      url: "#",
      items: [
        {
          title: "Active Proposals",
          url: "#",
        },
        {
          title: "Archived",
          url: "#",
        },
      ],
    },
  ],
  projects: [
    {
      name: "Data Library",
      url: "#",
      icon: (
        <FolderIcon />
      ),
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const [isMobile, setIsMobile] = React.useState(false);
  const { setOpenMobile } = useSidebar();

  // Détecter la taille de l'écran
  React.useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 768); // md breakpoint
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);

    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  // Fonction pour gérer les clics sur les liens de navigation
  const handleNavClick = () => {
    if (isMobile) {
      setOpenMobile(false);
    }
  };
  return (
    <Sidebar collapsible="offcanvas" {...props} className="max-w-[2/10]">
      <SidebarHeader >
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
            // className="data-[slot=sidebar-menu-button]:p-1.5!"
            >
              <Link href="#" onClick={handleNavClick}>
                <Code className="" />
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <h2 className="text-xl font-bold flex items-center">
                    <span className="text-primary">Nullify</span>
                  </h2>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavProjects items={data.projects} />
        {/* <NavSecondary items={data.navSecondary} className="mt-auto" /> */}
      </SidebarContent>
      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
    </Sidebar>
  )
}
