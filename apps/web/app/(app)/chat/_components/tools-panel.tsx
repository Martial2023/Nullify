"use client"

import { useEffect, useState } from "react"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Separator } from "@/components/ui/separator"
import { StatusBadge } from "@/components/StatusBadge"
import { SeverityBadge } from "@/components/SeverityBadge"
import { getScans } from "@/app/(actions)/scan"
import { getFindings } from "@/app/(actions)/finding"
import type { Scan, Finding } from "@/types"
import { Terminal, ShieldAlert, ScrollText } from "lucide-react"

const preventClose = (e: Event) => e.preventDefault()

export function ToolsPanel({
  projectId,
  open,
  onOpenChange,
}: {
  projectId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const [scans, setScans] = useState<Scan[]>([])
  const [findings, setFindings] = useState<Finding[]>([])

  useEffect(() => {
    if (open) {
      getScans(projectId).then(setScans).catch(console.error)
      getFindings(projectId).then(setFindings).catch(console.error)
    }
  }, [open, projectId])

  return (
    <Sheet open={open} onOpenChange={onOpenChange} modal={false}>
      <SheetContent
        side="right"
        overlay={false}
        onInteractOutside={preventClose}
        onPointerDownOutside={preventClose}
      >
        <SheetHeader>
          <SheetTitle>Tools & Findings</SheetTitle>
        </SheetHeader>

        <div className="flex flex-col gap-5 overflow-y-auto px-4 pb-4">
          <section className="space-y-2">
            <h3 className="flex items-center gap-1.5 text-xs font-medium uppercase text-muted-foreground">
              <Terminal className="size-3.5" />
              Scans
            </h3>
            {scans.length > 0 ? (
              <div className="space-y-2">
                {scans.map((s) => (
                  <div
                    key={s.id}
                    className="flex items-center justify-between rounded-md border p-2 text-xs"
                  >
                    <div className="space-y-0.5">
                      <p className="font-medium font-mono">{s.tool}</p>
                      <p className="text-muted-foreground truncate max-w-36">
                        {s.target}
                      </p>
                    </div>
                    <StatusBadge status={s.status} variant="scan" />
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No scans yet</p>
            )}
          </section>

          <Separator />

          <section className="space-y-2">
            <h3 className="flex items-center gap-1.5 text-xs font-medium uppercase text-muted-foreground">
              <ShieldAlert className="size-3.5" />
              Findings
            </h3>
            {findings.length > 0 ? (
              <div className="space-y-1.5">
                {findings.slice(0, 10).map((f) => (
                  <div
                    key={f.id}
                    className="flex items-start gap-2 rounded-md border p-2 text-xs"
                  >
                    <SeverityBadge severity={f.severity} className="shrink-0" />
                    <p className="line-clamp-2">{f.title}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-muted-foreground">No findings yet</p>
            )}
          </section>

          <Separator />

          <section className="space-y-2">
            <h3 className="flex items-center gap-1.5 text-xs font-medium uppercase text-muted-foreground">
              <ScrollText className="size-3.5" />
              Logs
            </h3>
            <p className="text-xs text-muted-foreground">
              Live logs will appear here during scan execution.
            </p>
          </section>
        </div>
      </SheetContent>
    </Sheet>
  )
}
