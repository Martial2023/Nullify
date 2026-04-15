import { SeverityBadge } from "@/components/SeverityBadge"
import { StatusBadge } from "@/components/StatusBadge"
import { Button } from "@/components/ui/button"
import type { Finding } from "@/types"
import { CheckCircle, XCircle, ArrowLeft } from "lucide-react"
import Link from "next/link"

function formatDate(date: Date) {
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export function FindingHeader({ finding }: { finding: Finding }) {
  return (
    <div className="space-y-3">
      <Link
        href="/findings"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-3.5" />
        Back to Findings
      </Link>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <SeverityBadge severity={finding.severity} />
            <StatusBadge status={finding.status} variant="finding" />
          </div>
          <h1 className="text-xl font-bold tracking-tight lg:text-2xl">
            {finding.title}
          </h1>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
            {finding.target && <span>Target: {finding.target}</span>}
            <span>Created: {formatDate(finding.createdAt)}</span>
            <span>Updated: {formatDate(finding.updatedAt)}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="gap-1.5">
            <CheckCircle className="size-3.5" />
            Mark Resolved
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5">
            <XCircle className="size-3.5" />
            False Positive
          </Button>
        </div>
      </div>
    </div>
  )
}
