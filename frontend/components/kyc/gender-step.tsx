"use client"

interface GenderStepProps {
  selectedGender: string | null
  onGenderSelect: (gender: string) => void
}

const GENDER_OPTIONS = [
  { value: "woman", label: "Woman", emoji: "👩" },
  { value: "man", label: "Man", emoji: "🙍" },
  { value: "non-binary", label: "Non-binary", emoji: "🧑" },
  { value: "prefer-not-to-say", label: "Prefer not to say", emoji: "🧘" },
]

export function GenderStep({ selectedGender, onGenderSelect }: GenderStepProps) {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">What's your gender?</h1>
        <p className="text-muted-foreground">We ask this to personalize the styling experience for you.</p>
      </div>

      <div className="space-y-3">
        {GENDER_OPTIONS.map((option) => (
          <button
            key={option.value}
            onClick={() => onGenderSelect(option.value)}
            className="flex w-full items-center gap-3 rounded-xl bg-muted p-4 text-left transition-colors hover:bg-muted/80"
          >
            <span className="text-2xl">{option.emoji}</span>
            <span className="text-base font-medium">{option.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
