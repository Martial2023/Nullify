"use client"

import { Bar, BarChart, XAxis, YAxis, CartesianGrid } from "recharts"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

const colorMap: Record<string, string> = {
  Critical: "var(--color-critical)",
  High: "var(--color-high)",
  Medium: "var(--color-medium)",
  Low: "var(--color-low)",
  Info: "var(--color-info)",
}

const chartConfig = {
  count: { label: "Findings" },
  critical: { label: "Critical", color: "oklch(0.637 0.237 25.331)" },
  high: { label: "High", color: "oklch(0.705 0.213 47.604)" },
  medium: { label: "Medium", color: "oklch(0.795 0.184 86.047)" },
  low: { label: "Low", color: "oklch(0.623 0.214 259.815)" },
  info: { label: "Info", color: "oklch(0.552 0.016 285.938)" },
} satisfies ChartConfig

export function SeverityChart({
  distribution,
}: {
  distribution: Record<string, number>
}) {
  const data = Object.entries(distribution).map(([key, count]) => ({
    severity: key.charAt(0) + key.slice(1).toLowerCase(),
    count,
    fill: colorMap[key.charAt(0) + key.slice(1).toLowerCase()],
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Findings by Severity</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="aspect-auto h-48">
          <BarChart data={data} layout="vertical">
            <CartesianGrid horizontal={false} />
            <YAxis
              dataKey="severity"
              type="category"
              tickLine={false}
              axisLine={false}
              width={70}
            />
            <XAxis type="number" allowDecimals={false} hide />
            <ChartTooltip content={<ChartTooltipContent hideLabel />} />
            <Bar dataKey="count" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
