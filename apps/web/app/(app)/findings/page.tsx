"use client"

import { useState, useEffect, useCallback } from "react"
import { getAllFindings } from "@/app/(actions)/finding"
import { EmptyState } from "@/components/EmptyState"
import { Pagination } from "@/components/Pagination"
import { LoadingSpinner } from "@/components/LoadingSpinner"
import { FindingsFilters } from "./_components/findings-filters"
import { FindingsTable } from "./_components/findings-table"
import { SearchX } from "lucide-react"
import type { Finding, Severity, FindingStatus } from "@/types"

const PAGE_SIZE = 10

export default function FindingsPage() {
  const [search, setSearch] = useState("")
  const [severity, setSeverity] = useState("ALL")
  const [status, setStatus] = useState("ALL")
  const [page, setPage] = useState(1)
  const [findings, setFindings] = useState<Finding[]>([])
  const [loading, setLoading] = useState(true)

  const fetchFindings = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getAllFindings({
        severity: severity !== "ALL" ? (severity as Severity) : undefined,
        status: status !== "ALL" ? (status as FindingStatus) : undefined,
        search: search || undefined,
      })
      setFindings(data)
    } catch (error) {
      console.error("Failed to fetch findings:", error)
    } finally {
      setLoading(false)
    }
  }, [severity, status, search])

  useEffect(() => {
    fetchFindings()
  }, [fetchFindings])

  const totalPages = Math.max(1, Math.ceil(findings.length / PAGE_SIZE))
  const paginated = findings.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  return (
    <main className="flex flex-col gap-4 p-4 lg:gap-6 lg:p-6">
      <h1 className="text-2xl font-bold tracking-tight">Findings</h1>
      <FindingsFilters
        search={search}
        onSearchChange={(v) => { setSearch(v); setPage(1) }}
        severity={severity}
        onSeverityChange={(v) => { setSeverity(v); setPage(1) }}
        status={status}
        onStatusChange={(v) => { setStatus(v); setPage(1) }}
      />
      {loading ? (
        <div className="flex justify-center py-16">
          <LoadingSpinner size="lg" />
        </div>
      ) : paginated.length > 0 ? (
        <>
          <FindingsTable findings={paginated} />
          <Pagination
            page={page}
            totalPages={totalPages}
            onPageChange={setPage}
            className="justify-center"
          />
        </>
      ) : (
        <EmptyState
          icon={SearchX}
          title="No findings found"
          description="Try adjusting your filters or run a scan to discover vulnerabilities."
        />
      )}
    </main>
  )
}
