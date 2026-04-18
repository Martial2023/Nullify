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
import type { Scan, Finding, ToolCall } from "@/types"
import type { ToolFinding } from "@/types/api"
import { Terminal, ShieldAlert, ScrollText, Loader2, Globe, Server, Bug, Info } from "lucide-react"

const preventClose = (e: Event) => e.preventDefault()

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "bg-red-600 text-white",
  HIGH: "bg-orange-600 text-white",
  MEDIUM: "bg-yellow-600 text-white",
  LOW: "bg-blue-600 text-white",
  INFO: "bg-zinc-600 text-white",
}

const FINDING_ICONS: Record<string, typeof Globe> = {
  subdomain: Globe,
  live_host: Server,
  open_port: Server,
  vulnerability: Bug,
}

function FindingLabel({ finding }: { finding: ToolFinding }) {
  const Icon = FINDING_ICONS[finding.type] ?? Info
  const severity = finding.severity?.toUpperCase()

  return (
    <div className="flex items-start gap-2 rounded-md border p-2 text-xs">
      <Icon className="size-3.5 shrink-0 mt-0.5 text-muted-foreground" />
      <div className="min-w-0 flex-1">
        {finding.title && <p className="font-medium">{finding.title}</p>}
        {finding.subdomain && <p className="font-mono text-muted-foreground">{finding.subdomain}</p>}
        {finding.url && <p className="font-mono text-muted-foreground truncate">{finding.url}</p>}
        {finding.port && <p className="text-muted-foreground">Port {finding.port} — {finding.service}</p>}
        {finding.description && <p className="text-muted-foreground line-clamp-2">{finding.description}</p>}
      </div>
      {severity && (
        <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold ${SEVERITY_COLORS[severity] ?? SEVERITY_COLORS.INFO}`}>
          {severity}
        </span>
      )}
    </div>
  )
}

export function ToolsPanel({
  projectId,
  open,
  onOpenChange,
  liveToolCalls = [],
  liveFindings = [],
}: {
  projectId: string
  open: boolean
  onOpenChange: (open: boolean) => void
  liveToolCalls?: ToolCall[]
  liveFindings?: ToolFinding[]
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
          {liveToolCalls.length > 0 && (
            <>
              <section className="space-y-2">
                <h3 className="flex items-center gap-1.5 text-xs font-medium uppercase text-muted-foreground">
                  <Loader2 className="size-3.5 animate-spin" />
                  Live Execution
                </h3>
                <div className="space-y-2">
                  {liveToolCalls.map((tc) => (
                    <div
                      key={tc.id}
                      className="rounded-lg border bg-zinc-950 p-3 font-mono text-xs text-zinc-300"
                    >
                      <div className="flex items-center gap-2">
                        {!tc.result && (
                          <Loader2 className="size-3 animate-spin text-emerald-400" />
                        )}
                        <span className="text-emerald-400">$ {tc.name}</span>
                        <span className="text-zinc-500 truncate">
                          {JSON.stringify(tc.args)}
                        </span>
                      </div>
                      {tc.result && (
                        <pre className="mt-2 max-h-48 overflow-y-auto text-zinc-400 whitespace-pre-wrap">
                          {tc.result}
                        </pre>
                      )}
                    </div>
                  ))}
                </div>
              </section>
              <Separator />
            </>
          )}

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
              Findings {liveFindings.length > 0 && (
                <span className="ml-auto text-emerald-400">{liveFindings.length}</span>
              )}
            </h3>
            {liveFindings.length > 0 ? (
              <div className="space-y-1.5">
                {liveFindings.map((f, i) => (
                  <FindingLabel key={`live-${i}`} finding={f} />
                ))}
              </div>
            ) : findings.length > 0 ? (
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
