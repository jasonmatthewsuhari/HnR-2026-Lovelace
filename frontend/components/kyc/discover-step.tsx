"use client"

import { Button } from "@/components/ui/button"

interface DiscoverStepProps {
  onNext: () => void
}

export function DiscoverStep({ onNext }: DiscoverStepProps) {
  return (
    <div className="flex min-h-[calc(100vh-8rem)] flex-col">
      <div className="flex-1 space-y-6">
        <div className="space-y-2 text-center">
          <h1 className="text-balance text-3xl font-bold tracking-tight">Discover outfits and wardrobes</h1>
          <p className="text-muted-foreground">Connect with your friends and the Fits community to get inspired.</p>
        </div>

        <div className="relative mx-auto mt-12 h-[400px] w-full max-w-md">
          <div className="absolute left-0 top-8 z-10 w-48 rotate-[-8deg] overflow-hidden rounded-2xl bg-card shadow-lg">
            <div className="aspect-[3/4] bg-gradient-to-br from-amber-100 to-amber-50" />
          </div>
          <div className="absolute left-1/2 top-0 z-20 w-48 -translate-x-1/2 overflow-hidden rounded-2xl bg-card shadow-xl">
            <div className="aspect-[3/4] bg-gradient-to-br from-blue-100 to-blue-50" />
          </div>
          <div className="absolute right-0 top-12 z-10 w-48 rotate-[8deg] overflow-hidden rounded-2xl bg-card shadow-lg">
            <div className="aspect-[3/4] bg-gradient-to-br from-rose-100 to-rose-50" />
          </div>
        </div>
      </div>

      <Button onClick={onNext} className="h-14 w-full rounded-full text-base font-medium">
        Next
      </Button>
    </div>
  )
}
