"use client"

import { useState } from "react"

interface LocationStepProps {
  onPermissionSelect: (permission: string) => void
}

export function LocationStep({ onPermissionSelect }: LocationStepProps) {
  const [showDialog, setShowDialog] = useState(false)

  const handleRequestLocation = () => {
    setShowDialog(true)
  }

  const handleAllow = () => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        console.log("[v0] Location granted:", position.coords)
        onPermissionSelect("allow")
      },
      (error) => {
        console.log("[v0] Location denied:", error.message)
        onPermissionSelect("deny")
      },
    )
  }

  const handleBlock = () => {
    setShowDialog(false)
    onPermissionSelect("deny")
  }
  // </CHANGE>

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-balance text-3xl font-bold tracking-tight">Dress according to the weather near you</h1>
        <p className="text-muted-foreground">
          We use your location to show you the right weather and make outfit suggestions.
        </p>
      </div>

      <div className="overflow-hidden rounded-2xl">
        <div className="aspect-[16/10] w-full bg-gradient-to-br from-green-100 via-blue-50 to-orange-50">
          <div className="flex h-full items-center justify-center text-sm text-muted-foreground">Map Preview</div>
        </div>
      </div>

      {!showDialog ? (
        <button
          onClick={handleRequestLocation}
          className="w-full rounded-lg bg-black px-6 py-4 text-center font-semibold text-white transition-colors hover:bg-black/90"
        >
          Enable Location
        </button>
      ) : (
        <div className="mx-auto max-w-sm rounded-lg border bg-white shadow-lg">
          <div className="flex items-start gap-3 border-b p-4">
            <svg className="mt-0.5 h-5 w-5 flex-shrink-0 text-muted-foreground" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
                clipRule="evenodd"
              />
            </svg>
            <div className="flex-1">
              <p className="text-sm">
                <span className="font-semibold">lovelace.app</span> wants to
              </p>
              <p className="text-sm font-semibold">Know your location</p>
            </div>
            <button
              onClick={() => setShowDialog(false)}
              className="flex-shrink-0 text-muted-foreground hover:text-foreground"
              aria-label="Close"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="flex gap-2 p-4">
            <button
              onClick={handleBlock}
              className="flex-1 rounded px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent"
            >
              Block
            </button>
            <button
              onClick={handleAllow}
              className="flex-1 rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
            >
              Allow
            </button>
          </div>
        </div>
      )}
      {/* </CHANGE> */}
    </div>
  )
}
