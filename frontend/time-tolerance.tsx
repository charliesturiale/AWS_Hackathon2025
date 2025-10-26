"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { Clock } from "lucide-react"

interface TimeToleranceProps {
  onToleranceChange?: (value: number) => void
}

export default function TimeTolerance({ onToleranceChange }: TimeToleranceProps) {
  const [tolerance, setTolerance] = useState([50]) // Default to middle (1.5x)

  const handleChange = (value: number[]) => {
    setTolerance(value)
    if (onToleranceChange) {
      // Convert to actual multiplier (1.0 to 2.0)
      const multiplier = (value[0] / 100) + 1.0
      onToleranceChange(multiplier)
    }
  }

  // Convert slider value (0-100) to display value (1.0-2.0)
  const getDisplayValue = (sliderValue: number) => {
    return ((sliderValue / 100) + 1.0).toFixed(1)
  }

  return (
    <Card className="p-6 shadow-lg border-2 border-border/50 bg-white/90 backdrop-blur">
      <div className="flex items-center gap-3 mb-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 shadow-sm">
          <Clock className="h-5 w-5 text-primary" />
        </div>
        <h2 className="text-xl font-display font-bold text-foreground">Time Tolerance</h2>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between text-sm font-medium text-muted-foreground mb-2">
          <span>Minimum</span>
          <span className="text-base font-bold text-primary">{getDisplayValue(tolerance[0])}x</span>
          <span>Maximum</span>
        </div>

        <Slider
          value={tolerance}
          onValueChange={handleChange}
          max={100}
          step={1}
          className="w-full"
        />

        <p className="text-sm text-muted-foreground text-center mt-4">
          Adjust how much extra time you're willing to spend for a safer route
        </p>
      </div>
    </Card>
  )
}
