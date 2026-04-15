"use client"

import { Bar, BarChart, CartesianGrid, XAxis } from "recharts"
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
import type { WeeklyTrendItem } from "@/app/(actions)/dashboard"

const chartConfig = {
  findings: { label: "Findings", color: "var(--chart-1)" },
} satisfies ChartConfig

export function TrendChart({ data }: { data: WeeklyTrendItem[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Weekly Trend</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="aspect-auto h-48">
          <BarChart data={data}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="week"
              tickLine={false}
              axisLine={false}
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar
              dataKey="findings"
              fill="var(--color-findings)"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
