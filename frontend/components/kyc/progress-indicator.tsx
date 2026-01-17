interface ProgressIndicatorProps {
  currentStep: number
  totalSteps: number
}

export function ProgressIndicator({ currentStep, totalSteps }: ProgressIndicatorProps) {
  const progress = (currentStep / totalSteps) * 100

  return (
    <div className="sticky top-0 z-10 bg-background px-6 py-4">
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium text-foreground">
          {currentStep} / {totalSteps}
        </span>
        <div className="relative h-1 flex-1 overflow-hidden rounded-full bg-muted">
          <div className="h-full bg-foreground transition-all duration-300" style={{ width: `${progress}%` }} />
        </div>
      </div>
    </div>
  )
}
