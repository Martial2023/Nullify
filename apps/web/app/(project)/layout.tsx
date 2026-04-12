import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { AppSidebar } from "./_components/app-sidebar"
import { SiteHeader } from "./_components/site-header"

type Props = {
    children: React.ReactNode
}
export default function Page({ children }: Props) {
  return (
    <SidebarProvider
    //   style={
    //     {
    //       "--sidebar-width": "calc(var(--spacing) * 72)",
    //       "--header-height": "calc(var(--spacing) * 12)",
    //     } as React.CSSProperties
    //   }
    >
      <AppSidebar variant="inset" />
      <SidebarInset  className="p-0 pb-12">
        {/* <SidebarTrigger className="m-1 p-2 fixed top-3 text-xl left-2 z-200" /> */}
        <SiteHeader />
        {children}
      </SidebarInset>
    </SidebarProvider>
  )
}