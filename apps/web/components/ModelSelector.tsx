"use client"

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { AI_MODELS } from "@/lib/models"

const grouped = AI_MODELS.reduce<Record<string, typeof AI_MODELS>>(
  (acc, model) => {
    ;(acc[model.provider] ??= []).push(model)
    return acc
  },
  {}
)

export function ModelSelector({
  value,
  onValueChange,
}: {
  value: string
  onValueChange: (id: string) => void
}) {
  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger className="w-44 text-xs cursor-pointer">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {Object.entries(grouped).map(([provider, models]) => (
          <SelectGroup key={provider}>
            <SelectLabel>{provider}</SelectLabel>
            {models.map((m) => (
              <SelectItem key={m.id} value={m.id}>
                {m.name}
              </SelectItem>
            ))}
          </SelectGroup>
        ))}
      </SelectContent>
    </Select>
  )
}
