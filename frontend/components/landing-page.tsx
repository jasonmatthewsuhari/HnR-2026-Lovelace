"use client"

import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"

interface LandingPageProps {
  onGetStarted: () => void
}

export function LandingPage({ onGetStarted }: LandingPageProps) {
  return (
    <div className="relative min-h-screen overflow-hidden" style={{ zIndex: 2 }}>
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/4 top-20 h-[400px] w-[400px] animate-float rounded-full bg-gradient-to-br from-purple-200/30 via-pink-100/20 to-transparent blur-[80px]" />
        <div
          className="absolute right-1/4 top-40 h-[500px] w-[500px] animate-float rounded-full bg-gradient-to-br from-blue-200/25 via-purple-100/20 to-transparent blur-[90px]"
          style={{ animationDelay: "1s" }}
        />
        <div
          className="absolute bottom-20 left-1/3 h-[350px] w-[350px] animate-float rounded-full bg-gradient-to-br from-pink-100/25 via-blue-100/15 to-transparent blur-[80px]"
          style={{ animationDelay: "2s" }}
        />
      </div>

      {/* Hero Section */}
      <div className="relative z-10 flex min-h-screen flex-col">
        <header className="glass-card border-b border-border/50">
          <div className="mx-auto flex h-16 max-w-7xl items-center justify-center px-6">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-300/80 via-pink-200/70 to-blue-200/60 shadow-sm" />
              <span className="font-serif text-2xl tracking-wide text-foreground/90">Lovelace</span>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex flex-1 items-center">
          <div className="mx-auto max-w-7xl px-6">
            <div className="mx-auto max-w-3xl text-center">
              <h1 className="mb-6 text-balance font-serif text-5xl leading-[1.1] tracking-tight text-foreground/90 md:text-7xl">
                Dress for the weather. <span className="gradient-text-otome italic">Style for you.</span>
              </h1>

              <p className="mb-12 text-pretty text-lg leading-relaxed text-muted-foreground md:text-xl">
                Discover personalized outfit suggestions based on real-time weather, connect with fashion lovers, and
                build your dream wardrobe.
              </p>

              <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
                <Button
                  size="lg"
                  onClick={onGetStarted}
                  className="otome-glow group h-12 gap-2 rounded-full bg-gradient-to-r from-purple-300/90 via-pink-200/80 to-blue-200/70 px-8 text-base text-foreground hover:from-purple-300 hover:via-pink-200 hover:to-blue-200"
                >
                  Get Started
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </div>

              <div className="mt-24 grid gap-8 text-center sm:grid-cols-3">
                <div className="glass-card group rounded-3xl p-6 transition-all hover:scale-105">
                  <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-purple-200/80 to-pink-200/70 shadow-sm">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="text-foreground/80"
                    >
                      <path d="M12 2v10" />
                      <path d="m4.93 10.93 1.41 1.41" />
                      <path d="M2 18h2" />
                      <path d="M20 18h2" />
                      <path d="m19.07 10.93-1.41 1.41" />
                      <path d="M22 22H2" />
                      <path d="m16 6-4 4-4-4" />
                      <path d="M16 18a4 4 0 0 0-8 0" />
                    </svg>
                  </div>
                  <h3 className="mb-2 font-serif text-lg font-semibold text-foreground/90">Weather-Smart</h3>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    Get outfit suggestions that match the weather in your location.
                  </p>
                </div>

                <div className="glass-card group rounded-3xl p-6 transition-all hover:scale-105">
                  <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-blue-200/70 to-purple-200/60 shadow-sm">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="text-foreground/80"
                    >
                      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                      <circle cx="9" cy="7" r="4" />
                      <path d="M22 22H2" />
                      <path d="m16 6-4 4-4-4" />
                      <path d="M16 18a4 4 0 0 1 0 7.75" />
                    </svg>
                  </div>
                  <h3 className="mb-2 font-serif text-lg font-semibold text-foreground/90">Community-Driven</h3>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    Discover outfits and wardrobes from friends and fashion enthusiasts.
                  </p>
                </div>

                <div className="glass-card group rounded-3xl p-6 transition-all hover:scale-105">
                  <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-pink-200/70 to-purple-200/60 shadow-sm">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="text-foreground/80"
                    >
                      <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  </div>
                  <h3 className="mb-2 font-serif text-lg font-semibold text-foreground/90">Personalized</h3>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    Build your wardrobe and get styling tailored to your preferences.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="glass-card border-t border-border/50 py-8">
          <div className="mx-auto max-w-7xl px-6 text-center text-sm text-muted-foreground">
            © 2025 Lovelace. All rights reserved.
          </div>
        </footer>
      </div>
    </div>
  )
}
