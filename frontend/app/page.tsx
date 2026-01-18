"use client"

import { useState, useEffect } from "react"
import { LandingPage } from "@/components/landing-page"
import { AuthScreen } from "@/components/auth-screen"
import { KYCOnboarding } from "@/components/kyc-onboarding"
import { FashionLoadingScreen } from "@/components/fashion-loading-screen"
import { MainApp } from "@/components/main-app"
import { useAuth } from "@/hooks/use-auth"

export default function Home() {
  const { user, userProfile, loading } = useAuth()
  const [showAuth, setShowAuth] = useState(false)
  const [showKYC, setShowKYC] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [showMainApp, setShowMainApp] = useState(false)

  // Check if user is already authenticated on mount
  useEffect(() => {
    if (!loading && user && userProfile !== null) {
      // User is already logged in and profile has loaded
      if (userProfile.onboardingCompleted) {
        // User has completed onboarding, show main app
        setShowMainApp(true)
      } else {
        // User needs to complete onboarding
        setShowKYC(true)
      }
    }
  }, [loading, user, userProfile])

  // Show loading screen while checking auth state
  if (loading) {
    return (
      <FashionLoadingScreen
        onComplete={() => {
          // This won't be called, but required by component
        }}
      />
    )
  }

  if (isLoading) {
    return (
      <FashionLoadingScreen
        onComplete={() => {
          setIsLoading(false)
          setShowAuth(true)
        }}
      />
    )
  }

  if (showMainApp) {
    return <MainApp />
  }

  if (showKYC) {
    return <KYCOnboarding onComplete={() => setShowMainApp(true)} />
  }

  if (showAuth) {
    return (
      <AuthScreen
        onSignup={() => setShowKYC(true)}
        onLogin={() => setShowMainApp(true)}
      />
    )
  }

  return <LandingPage onGetStarted={() => setIsLoading(true)} />
}
