"use client"

import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Search } from "lucide-react"
import { Severity, FindingStatus } from "@/types"

const severities = Object.values(Severity)
const statuses = Object.values(FindingStatus)

const statusLabels: Record<string, string> = {
  OPEN: "Open",
  CONFIRMED: "Confirmed",
  FALSE_POSITIVE: "False Positive",
  RESOLVED: "Resolved",
}

export function FindingsFilters({
  search,
  onSearchChange,
  severity,
  onSeverityChange,
  status,
  onStatusChange,
}: {
  search: string
  onSearchChange: (v: string) => void
  severity: string
  onSeverityChange: (v: string) => void
  status: string
  onStatusChange: (v: string) => void
}) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="relative flex-1 min-w-48">
        <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
        <Input
          placeholder="Search findings..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-9"
        />
      </div>
      <Select value={severity} onValueChange={onSeverityChange}>
        <SelectTrigger className="w-36">
          <SelectValue placeholder="Severity" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="ALL">All Severities</SelectItem>
          {severities.map((s) => (
            <SelectItem key={s} value={s}>
              {s.charAt(0) + s.slice(1).toLowerCase()}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select value={status} onValueChange={onStatusChange}>
        <SelectTrigger className="w-36">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="ALL">All Statuses</SelectItem>
          {statuses.map((s) => (
            <SelectItem key={s} value={s}>
              {statusLabels[s] ?? s}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
