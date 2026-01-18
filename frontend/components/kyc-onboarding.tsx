"use client"

import { useState } from "react"
import { UsernameStep } from "@/components/kyc/username-step"
import { GenderStep } from "@/components/kyc/gender-step"
import { BodySizeStep } from "@/components/kyc/body-size-step"
import { SuggestedPiecesStep } from "@/components/kyc/suggested-pieces-step"
import { ProgressIndicator } from "@/components/kyc/progress-indicator"
import { NameStep } from "@/components/kyc/name-step"
import { BoyfriendSelectionStep } from "@/components/kyc/boyfriend-selection-step"

const TOTAL_STEPS = 6

interface KYCOnboardingProps {
  onComplete?: () => void
}

export function KYCOnboarding({ onComplete }: KYCOnboardingProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    username: "",
    gender: null as string | null,
    bodySizeData: {},
    selectedPieces: [] as string[],
    selectedBoyfriend: null as any,
    customBoyfriendImage: null as File | null,
  })

  const handleNext = () => {
    if (currentStep < TOTAL_STEPS) {
      setCurrentStep(currentStep + 1)
    } else if (currentStep === TOTAL_STEPS && onComplete) {
      handleComplete()
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

  const handleComplete = async () => {
    try {
      // Prepare data for storage - keep the full boyfriend object or just the ID
      const dataToSave = {
        ...formData,
        // If it's a string, keep it; if it's an object, save the whole object for custom boyfriends
        // Otherwise default to 'alex'
        selectedBoyfriend: formData.selectedBoyfriend 
          ? (typeof formData.selectedBoyfriend === 'string' 
            ? formData.selectedBoyfriend 
            : formData.selectedBoyfriend)  // Keep the full object for custom boyfriends
          : 'alex'
      }
      
      console.log('Saving to localStorage:', dataToSave)
      
      // Save to localStorage
      localStorage.setItem("lovelace-user-profile", JSON.stringify(dataToSave))

      // Update Firestore to mark onboarding as completed
      const { doc, updateDoc } = await import('firebase/firestore')
      const { db } = await import('@/lib/firebase')
      const { getCurrentUser } = await import('@/lib/auth')

      const user = getCurrentUser()
      if (user) {
        const userDocRef = doc(db, 'users', user.uid)
        await updateDoc(userDocRef, {
          ...dataToSave,
          onboardingCompleted: true,
          updatedAt: new Date(),
        })
      }

      if (onComplete) {
        onComplete()
      }
    } catch (error) {
      console.error('Error completing onboarding:', error)
      // Still proceed even if Firestore update fails
      if (onComplete) {
        onComplete()
      }
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
            <GenderStep
              selectedGender={formData.gender}
              onGenderSelect={(gender) => {
                updateFormData({ gender })
                handleNext()
              }}
            />
          )}

          {currentStep === 4 && (
            <BodySizeStep
              bodySizeData={formData.bodySizeData}
              onBodySizeChange={(bodySizeData) => updateFormData({ bodySizeData })}
              onNext={handleNext}
            />
          )}

          {currentStep === 5 && (
            <BoyfriendSelectionStep
              selectedBoyfriend={formData.selectedBoyfriend}
              onBoyfriendSelect={(boyfriend) => updateFormData({
                selectedBoyfriend: boyfriend,
                customBoyfriendImage: boyfriend ? null : formData.customBoyfriendImage
              })}
              onImageUpload={(file) => updateFormData({ customBoyfriendImage: file })}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}

          {currentStep === 6 && (
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
