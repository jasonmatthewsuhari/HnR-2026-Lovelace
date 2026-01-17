"use client"

import { useState } from "react"
import { LandingPage } from "@/components/landing-page"
import { AuthScreen } from "@/components/auth-screen"
import { KYCOnboarding } from "@/components/kyc-onboarding"
import { FashionLoadingScreen } from "@/components/fashion-loading-screen"
import { MainApp } from "@/components/main-app"

export default function Home() {
  const [showAuth, setShowAuth] = useState(false)
  const [showKYC, setShowKYC] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [showMainApp, setShowMainApp] = useState(false)

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
