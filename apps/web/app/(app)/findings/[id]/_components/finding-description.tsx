import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { Finding } from "@/types"

export function FindingDescription({ finding }: { finding: Finding }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Description</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm leading-relaxed">{finding.description}</p>
        {finding.evidence && (
          <div className="space-y-1.5">
            <h4 className="text-sm font-medium">Evidence</h4>
            <pre className="overflow-x-auto rounded-lg bg-muted p-4 font-mono text-xs">
              {finding.evidence}
            </pre>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
