"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

interface BodySizeStepProps {
  bodySizeData: {
    height?: string
    topSize?: string
    bottomSize?: string
    shoeSize?: string
    bodyType?: string
  }
  onBodySizeChange: (data: any) => void
  onNext: () => void
}

const HEIGHT_OPTIONS = [
  "Under 5'0\"",
  "5'0\" - 5'3\"",
  "5'4\" - 5'7\"",
  "5'8\" - 5'11\"",
  "6'0\" - 6'3\"",
  "Over 6'3\"",
]

const TOP_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL"]

const BOTTOM_SIZES = ["24", "26", "28", "30", "32", "34", "36", "38", "40", "42"]

const SHOE_SIZES = ["5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]

const BODY_TYPES = [
  { value: "athletic", label: "Athletic", emoji: "💪" },
  { value: "slim", label: "Slim", emoji: "🌿" },
  { value: "curvy", label: "Curvy", emoji: "✨" },
  { value: "plus", label: "Plus Size", emoji: "🌟" },
  { value: "average", label: "Average", emoji: "👤" },
]

export function BodySizeStep({ bodySizeData, onBodySizeChange, onNext }: BodySizeStepProps) {
  const [data, setData] = useState(bodySizeData)

  const updateData = (field: string, value: string) => {
    const newData = { ...data, [field]: value }
    setData(newData)
    onBodySizeChange(newData)
  }

  const isComplete = data.height && data.topSize && data.bottomSize && data.shoeSize && data.bodyType

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Tell us your sizes</h1>
        <p className="text-muted-foreground">This helps us find the perfect fit for you.</p>
      </div>

      {/* Body Type */}
      <div className="space-y-3">
        <label className="text-sm font-medium">Body Type</label>
        <div className="grid grid-cols-2 gap-2">
          {BODY_TYPES.map((type) => (
            <button
              key={type.value}
              onClick={() => updateData("bodyType", type.value)}
              className={`flex items-center gap-2 rounded-lg border-2 p-3 text-left transition-all ${
                data.bodyType === type.value
                  ? "border-foreground bg-foreground/5"
                  : "border-border bg-background hover:border-foreground/50"
              }`}
            >
              <span className="text-xl">{type.emoji}</span>
              <span className="text-sm font-medium">{type.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Height */}
      <div className="space-y-3">
        <label className="text-sm font-medium">Height</label>
        <div className="grid grid-cols-2 gap-2">
          {HEIGHT_OPTIONS.map((height) => (
            <button
              key={height}
              onClick={() => updateData("height", height)}
              className={`rounded-lg border-2 px-4 py-3 text-sm font-medium transition-all ${
                data.height === height
                  ? "border-foreground bg-foreground/5"
                  : "border-border bg-background hover:border-foreground/50"
              }`}
            >
              {height}
            </button>
          ))}
        </div>
      </div>

      {/* Top Size */}
      <div className="space-y-3">
        <label className="text-sm font-medium">Top Size</label>
        <div className="grid grid-cols-4 gap-2">
          {TOP_SIZES.map((size) => (
            <button
              key={size}
              onClick={() => updateData("topSize", size)}
              className={`rounded-lg border-2 px-4 py-3 text-sm font-medium transition-all ${
                data.topSize === size
                  ? "border-foreground bg-foreground/5"
                  : "border-border bg-background hover:border-foreground/50"
              }`}
            >
              {size}
            </button>
          ))}
        </div>
      </div>

      {/* Bottom Size */}
      <div className="space-y-3">
        <label className="text-sm font-medium">Bottom Size (Waist)</label>
        <div className="grid grid-cols-5 gap-2">
          {BOTTOM_SIZES.map((size) => (
            <button
              key={size}
              onClick={() => updateData("bottomSize", size)}
              className={`rounded-lg border-2 px-4 py-3 text-sm font-medium transition-all ${
                data.bottomSize === size
                  ? "border-foreground bg-foreground/5"
                  : "border-border bg-background hover:border-foreground/50"
              }`}
            >
              {size}
            </button>
          ))}
        </div>
      </div>

      {/* Shoe Size */}
      <div className="space-y-3">
        <label className="text-sm font-medium">Shoe Size (US)</label>
        <div className="grid grid-cols-5 gap-2">
          {SHOE_SIZES.map((size) => (
            <button
              key={size}
              onClick={() => updateData("shoeSize", size)}
              className={`rounded-lg border-2 px-4 py-3 text-sm font-medium transition-all ${
                data.shoeSize === size
                  ? "border-foreground bg-foreground/5"
                  : "border-border bg-background hover:border-foreground/50"
              }`}
            >
              {size}
            </button>
          ))}
        </div>
      </div>

      <Button
        onClick={onNext}
        disabled={!isComplete}
        className="w-full rounded-full py-6 text-base font-medium"
        size="lg"
      >
        Next
      </Button>
    </div>
  )
}
