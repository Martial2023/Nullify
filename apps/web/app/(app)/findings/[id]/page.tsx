export const dynamic = "force-dynamic"

import { getFinding } from "@/app/(actions)/finding"
import { EmptyState } from "@/components/EmptyState"
import { SearchX } from "lucide-react"
import { FindingHeader } from "./_components/finding-header"
import { FindingDescription } from "./_components/finding-description"
import { FindingRemediation } from "./_components/finding-remediation"
import { FindingActivity } from "./_components/finding-activity"

export default async function FindingDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const finding = await getFinding(id)

  if (!finding) {
    return (
      <main className="p-4 lg:p-6">
        <EmptyState
          icon={SearchX}
          title="Finding not found"
          description="This finding doesn't exist or has been removed."
        />
      </main>
    )
  }

  return (
    <main className="flex flex-col gap-4 p-4 lg:gap-6 lg:p-6">
      <FindingHeader finding={finding} />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="flex flex-col gap-4 lg:col-span-2">
          <FindingDescription finding={finding} />
          <FindingRemediation finding={finding} />
        </div>
        <FindingActivity finding={finding} />
      </div>
    </main>
  )
}
