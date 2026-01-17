"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

interface NameStepProps {
  firstName: string
  lastName: string
  onNameChange: (firstName: string, lastName: string) => void
  onNext: () => void
}

export function NameStep({ firstName, lastName, onNameChange, onNext }: NameStepProps) {
  const [localFirstName, setLocalFirstName] = useState(firstName)
  const [localLastName, setLocalLastName] = useState(lastName)

  const handleNext = () => {
    if (localFirstName.trim() && localLastName.trim()) {
      onNameChange(localFirstName, localLastName)
      onNext()
    }
  }

  const isValid = localFirstName.trim().length > 0 && localLastName.trim().length > 0

  return (
    <div className="space-y-6">
      <div>
        <h2 className="mb-2 text-3xl font-bold">What's your name?</h2>
        <p className="text-muted-foreground">Let's get to know you better.</p>
      </div>

      <div className="space-y-4">
        <div>
          <label htmlFor="firstName" className="mb-2 block text-sm font-medium text-muted-foreground">
            First name
          </label>
          <input
            id="firstName"
            type="text"
            value={localFirstName}
            onChange={(e) => setLocalFirstName(e.target.value)}
            placeholder="Enter your first name"
            className="w-full rounded-2xl border-2 border-border bg-background px-6 py-4 text-lg focus:border-foreground focus:outline-none"
          />
        </div>

        <div>
          <label htmlFor="lastName" className="mb-2 block text-sm font-medium text-muted-foreground">
            Last name
          </label>
          <input
            id="lastName"
            type="text"
            value={localLastName}
            onChange={(e) => setLocalLastName(e.target.value)}
            placeholder="Enter your last name"
            className="w-full rounded-2xl border-2 border-border bg-background px-6 py-4 text-lg focus:border-foreground focus:outline-none"
          />
        </div>
      </div>

      <Button onClick={handleNext} disabled={!isValid} className="w-full rounded-full py-6 text-lg" size="lg">
        Next
      </Button>
    </div>
  )
}
