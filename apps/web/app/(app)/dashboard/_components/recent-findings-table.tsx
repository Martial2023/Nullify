import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { SeverityBadge } from "@/components/SeverityBadge"
import { StatusBadge } from "@/components/StatusBadge"
import { EmptyState } from "@/components/EmptyState"
import { ShieldAlert } from "lucide-react"
import type { Severity } from "@/types"
import Link from "next/link"

function formatDate(date: Date) {
  return new Date(date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  })
}

interface RecentFinding {
  id: string
  severity: Severity
  status: string
  title: string
  target: string | null
  createdAt: Date
}

export function RecentFindingsTable({
  findings,
}: {
  findings: RecentFinding[]
}) {
  if (findings.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Findings</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            icon={ShieldAlert}
            title="No findings yet"
            description="Findings will appear here after running scans."
          />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Findings</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-28">Severity</TableHead>
              <TableHead>Title</TableHead>
              <TableHead className="hidden md:table-cell">Target</TableHead>
              <TableHead className="w-32">Status</TableHead>
              <TableHead className="w-24 text-right">Date</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {findings.map((f) => (
              <TableRow key={f.id}>
                <TableCell>
                  <SeverityBadge severity={f.severity} />
                </TableCell>
                <TableCell>
                  <Link
                    href={`/findings/${f.id}`}
                    className="font-medium hover:underline"
                  >
                    {f.title}
                  </Link>
                </TableCell>
                <TableCell className="hidden max-w-48 truncate text-muted-foreground md:table-cell">
                  {f.target}
                </TableCell>
                <TableCell>
                  <StatusBadge status={f.status} variant="finding" />
                </TableCell>
                <TableCell className="text-right text-muted-foreground">
                  {formatDate(f.createdAt)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
