"use client"

import { Button } from "@/components/ui/button"

interface SuggestedPiecesStepProps {
  selectedPieces: string[]
  onPiecesChange: (pieces: string[]) => void
  onSkip: () => void
}

const SUGGESTED_ITEMS = [
  { id: "nike-air-force", name: "Nike Air Force 1", image: "/placeholder.svg?height=200&width=200" },
  { id: "basic-jeans", name: "Basic Jeans", image: "/placeholder.svg?height=200&width=200" },
  { id: "adidas-campus", name: "Adidas Campus", image: "/placeholder.svg?height=200&width=200" },
  { id: "basic-tshirt", name: "Basic T-Shirt", image: "/placeholder.svg?height=200&width=200" },
  { id: "black-jeans", name: "Black Jeans", image: "/placeholder.svg?height=200&width=200" },
  { id: "black-sneakers", name: "Black Sneakers", image: "/placeholder.svg?height=200&width=200" },
]

export function SuggestedPiecesStep({ selectedPieces, onPiecesChange, onSkip }: SuggestedPiecesStepProps) {
  const togglePiece = (id: string) => {
    if (selectedPieces.includes(id)) {
      onPiecesChange(selectedPieces.filter((p) => p !== id))
    } else {
      onPiecesChange([...selectedPieces, id])
    }
  }

  const hasSelection = selectedPieces.length > 0

  return (
    <div className="flex min-h-[calc(100vh-8rem)] flex-col">
      <div className="flex-1 space-y-6">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Add suggested pieces</h1>
          <p className="text-muted-foreground">
            Fits is more fun when you've added a few clothes. Add some of these to start.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {SUGGESTED_ITEMS.map((item) => (
            <button
              key={item.id}
              onClick={() => togglePiece(item.id)}
              className="group relative overflow-hidden rounded-2xl bg-muted transition-all hover:bg-muted/80"
            >
              <div className="aspect-square p-4">
                <img src={item.image || "/placeholder.svg"} alt={item.name} className="h-full w-full object-contain" />
              </div>
              <div className="p-3">
                <p className="text-sm font-medium">{item.name}</p>
              </div>
              <div className="absolute right-3 top-3">
                <div
                  className={`h-6 w-6 rounded-full border-2 transition-colors ${
                    selectedPieces.includes(item.id)
                      ? "border-foreground bg-foreground"
                      : "border-muted-foreground/30 bg-background"
                  }`}
                >
                  {selectedPieces.includes(item.id) && (
                    <svg
                      className="h-full w-full text-background"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <Button
        onClick={onSkip}
        disabled={!hasSelection}
        variant="ghost"
        className="mt-6 h-14 w-full text-base font-medium"
      >
        Continue
      </Button>
    </div>
  )
}
