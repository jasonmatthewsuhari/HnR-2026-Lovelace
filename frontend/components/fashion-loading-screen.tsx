"use client"

import { useEffect, useState } from "react"

interface FashionLoadingScreenProps {
  onComplete: () => void
}

export function FashionLoadingScreen({ onComplete }: FashionLoadingScreenProps) {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const duration = 2000
    const interval = 20
    const steps = duration / interval
    let currentStep = 0

    const timer = setInterval(() => {
      currentStep++
      setProgress((currentStep / steps) * 100)

      if (currentStep >= steps) {
        clearInterval(timer)
        setTimeout(onComplete, 200)
      }
    }, interval)

    return () => clearInterval(timer)
  }, [onComplete])

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background">
      {/* Animated clothing items */}
      <div className="relative">
        {/* Center logo */}
        <div className="mb-12 flex flex-col items-center gap-4">
          <div className="relative">
            {/* Spinning hanger */}
            <div className="animate-spin-slow">
              <svg
                width="80"
                height="80"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-foreground"
              >
                {/* Hanger hook */}
                <path d="M12 2v3" />
                <circle cx="12" cy="5" r="1" />
                {/* Hanger bar */}
                <path d="M3 14h18" />
                <path d="M4 14l8-6 8 6" />
              </svg>
            </div>

            {/* Orbiting fashion items */}
            <div className="absolute inset-0 animate-orbit">
              <div className="absolute -top-12 left-1/2 h-6 w-6 -translate-x-1/2 text-muted-foreground/40">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" />
                  <path d="M2 17L12 22L22 17" />
                  <path d="M2 12L12 17L22 12" />
                </svg>
              </div>
            </div>

            <div className="absolute inset-0 animate-orbit-reverse">
              <div className="absolute -bottom-12 left-1/2 h-6 w-6 -translate-x-1/2 text-muted-foreground/40">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 8v8" stroke="white" strokeWidth="1.5" />
                  <path d="M8 12h8" stroke="white" strokeWidth="1.5" />
                </svg>
              </div>
            </div>
          </div>

          <div className="text-center">
            <h2 className="mb-2 font-serif text-2xl tracking-tight">Lovelace</h2>
            <p className="text-sm text-muted-foreground">Preparing your style journey...</p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mx-auto w-64">
          <div className="h-1 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full bg-foreground transition-all duration-200 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Background effects */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 animate-pulse rounded-full bg-accent/10 blur-3xl" />
      </div>
    </div>
  )
}
