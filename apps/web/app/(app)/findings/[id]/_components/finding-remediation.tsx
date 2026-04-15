import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { Finding } from "@/types"

export function FindingRemediation({ finding }: { finding: Finding }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Remediation</CardTitle>
      </CardHeader>
      <CardContent>
        {finding.remediation ? (
          <p className="text-sm leading-relaxed">{finding.remediation}</p>
        ) : (
          <p className="text-sm text-muted-foreground">
            No remediation available for this finding.
          </p>
        )}
      </CardContent>
    </Card>
  )
}
