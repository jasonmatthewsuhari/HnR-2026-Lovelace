"use client"

import { useState } from "react"
import { UsernameStep } from "@/components/kyc/username-step"
import { LocationStep } from "@/components/kyc/location-step"
import { GenderStep } from "@/components/kyc/gender-step"
import { BodySizeStep } from "@/components/kyc/body-size-step"
import { DiscoverStep } from "@/components/kyc/discover-step"
import { SuggestedPiecesStep } from "@/components/kyc/suggested-pieces-step"
import { ProgressIndicator } from "@/components/kyc/progress-indicator"
import { NameStep } from "@/components/kyc/name-step"

const TOTAL_STEPS = 7

interface KYCOnboardingProps {
  onComplete?: () => void
}

export function KYCOnboarding({ onComplete }: KYCOnboardingProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    username: "",
    locationPermission: null as string | null,
    gender: null as string | null,
    bodySizeData: {},
    selectedPieces: [] as string[],
  })

  const handleNext = () => {
    if (currentStep < TOTAL_STEPS) {
      setCurrentStep(currentStep + 1)
    } else if (currentStep === TOTAL_STEPS && onComplete) {
      onComplete()
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const updateFormData = (data: Partial<typeof formData>) => {
    setFormData((prev) => ({ ...prev, ...data }))
  }

  const handleComplete = () => {
    localStorage.setItem("lovelace-user-profile", JSON.stringify(formData))
    if (onComplete) {
      onComplete()
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-2xl">
        <ProgressIndicator currentStep={currentStep} totalSteps={TOTAL_STEPS} />

        <div className="p-6">
          {currentStep === 1 && (
            <NameStep
              firstName={formData.firstName}
              lastName={formData.lastName}
              onNameChange={(firstName, lastName) => updateFormData({ firstName, lastName })}
              onNext={handleNext}
            />
          )}

          {currentStep === 2 && (
            <UsernameStep
              username={formData.username}
              onUsernameChange={(username) => updateFormData({ username })}
              onNext={handleNext}
            />
          )}

          {currentStep === 3 && (
            <LocationStep
              onPermissionSelect={(permission) => {
                updateFormData({ locationPermission: permission })
                handleNext()
              }}
            />
          )}

          {currentStep === 4 && (
            <GenderStep
              selectedGender={formData.gender}
              onGenderSelect={(gender) => {
                updateFormData({ gender })
                handleNext()
              }}
            />
          )}

          {currentStep === 5 && (
            <BodySizeStep
              bodySizeData={formData.bodySizeData}
              onBodySizeChange={(bodySizeData) => updateFormData({ bodySizeData })}
              onNext={handleNext}
            />
          )}

          {currentStep === 6 && <DiscoverStep onNext={handleNext} />}

          {currentStep === 7 && (
            <SuggestedPiecesStep
              selectedPieces={formData.selectedPieces}
              onPiecesChange={(pieces) => updateFormData({ selectedPieces: pieces })}
              onSkip={handleComplete}
            />
          )}
        </div>
      </div>
    </div>
  )
}
