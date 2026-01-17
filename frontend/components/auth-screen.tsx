"use client"

import { useState } from "react"
import { Chrome, ArrowRight, AlertCircle, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { signInWithGoogle, signInWithEmail, signUpWithEmail, resetPassword } from "@/lib/auth"

interface AuthScreenProps {
  onSignup: () => void
  onLogin: () => void
}

export function AuthScreen({ onSignup, onLogin }: AuthScreenProps) {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [showForgotPassword, setShowForgotPassword] = useState(false)
  const [resetEmailSent, setResetEmailSent] = useState(false)

  const handleGoogleAuth = async () => {
    setError("")
    setLoading(true)
    
    try {
      const { user, error: authError, isNewUser } = await signInWithGoogle()
      
      if (authError) {
        setError(authError)
        setLoading(false)
        return
      }

      if (user) {
        // Store user info in localStorage for easy access
        localStorage.setItem("lovelace_user_id", user.uid)
        localStorage.setItem("lovelace_user_email", user.email || "")
        
        // Check if user needs onboarding
        if (isNewUser) {
          onSignup() // New user - go to KYC
        } else {
          onLogin() // Existing user - go to main app
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to sign in with Google")
      setLoading(false)
    }
  }

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    
    try {
      if (isLogin) {
        // Sign in existing user
        const { user, error: authError } = await signInWithEmail(email, password)
        
        if (authError) {
          setError(authError)
          setLoading(false)
          return
        }

        if (user) {
          localStorage.setItem("lovelace_user_id", user.uid)
          localStorage.setItem("lovelace_user_email", user.email || "")
          onLogin() // Go to main app
        }
      } else {
        // Sign up new user
        const { user, error: authError } = await signUpWithEmail(email, password, name)
        
        if (authError) {
          setError(authError)
          setLoading(false)
          return
        }

        if (user) {
          localStorage.setItem("lovelace_user_id", user.uid)
          localStorage.setItem("lovelace_user_email", user.email || "")
          localStorage.setItem("lovelace_user_name", name)
          onSignup() // Go to KYC onboarding
        }
      }
    } catch (err: any) {
      setError(err.message || "An error occurred")
      setLoading(false)
    }
  }

  const handleForgotPassword = async () => {
    if (!email) {
      setError("Please enter your email address")
      return
    }

    setError("")
    setLoading(true)

    const { error: resetError } = await resetPassword(email)

    setLoading(false)

    if (resetError) {
      setError(resetError)
    } else {
      setResetEmailSent(true)
      setTimeout(() => {
        setResetEmailSent(false)
        setShowForgotPassword(false)
      }, 3000)
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden" style={{ zIndex: 2 }}>
      {/* Background blobs */}
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

      {/* Main Content */}
      <div className="relative z-10 flex min-h-screen flex-col">
        <header className="glass-card border-b border-border/50">
          <div className="mx-auto flex h-16 max-w-7xl items-center justify-center px-6">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-300/80 via-pink-200/70 to-blue-200/60 shadow-sm" />
              <span className="font-serif text-2xl tracking-wide text-foreground/90">Lovelace</span>
            </div>
          </div>
        </header>

        <main className="flex flex-1 items-center justify-center p-6">
          <div className="glass-card w-full max-w-md rounded-3xl p-8 shadow-xl">
            <div className="mb-8 text-center">
              <h1 className="mb-2 font-serif text-3xl font-bold text-foreground/90">
                {showForgotPassword ? "Reset Password" : isLogin ? "Welcome back" : "Join Lovelace"}
              </h1>
              <p className="text-sm text-muted-foreground">
                {showForgotPassword
                  ? "Enter your email to receive a password reset link"
                  : isLogin
                  ? "Log in to continue your fashion journey"
                  : "Create an account to get personalized outfit recommendations"}
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-4 flex items-start gap-2 rounded-2xl bg-destructive/10 p-4 text-sm text-destructive">
                <AlertCircle className="h-5 w-5 flex-shrink-0" />
                <p>{error}</p>
              </div>
            )}

            {/* Success Message */}
            {resetEmailSent && (
              <div className="mb-4 rounded-2xl bg-green-500/10 p-4 text-sm text-green-600">
                Password reset email sent! Check your inbox.
              </div>
            )}

            {/* Forgot Password View */}
            {showForgotPassword ? (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="reset-email">Email</Label>
                  <Input
                    id="reset-email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="rounded-full border-2 py-6"
                  />
                </div>

                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowForgotPassword(false)
                      setError("")
                    }}
                    className="flex-1 rounded-full py-6"
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleForgotPassword}
                    disabled={loading || !email}
                    className="otome-glow flex-1 gap-2 rounded-full bg-gradient-to-r from-purple-300/90 via-pink-200/80 to-blue-200/70 py-6 text-foreground hover:from-purple-300 hover:via-pink-200 hover:to-blue-200"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      "Send Reset Link"
                    )}
                  </Button>
                </div>
              </div>
            ) : (
              <>
                {/* Social Login Buttons */}
                <div className="space-y-3">
                  <Button
                    onClick={handleGoogleAuth}
                    disabled={loading}
                    variant="outline"
                    className="otome-glow w-full gap-2 rounded-full border-2 py-6 transition-all hover:scale-[1.02] disabled:opacity-50"
                  >
                    {loading ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <Chrome className="h-5 w-5" />
                    )}
                    Continue with Google
                  </Button>

                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-border"></div>
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                      <span className="bg-background px-2 text-muted-foreground">Or continue with email</span>
                    </div>
                  </div>
                </div>

                {/* Email/Password Form */}
                <form onSubmit={handleEmailAuth} className="mt-6 space-y-4">
                  {!isLogin && (
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name</Label>
                      <Input
                        id="name"
                        type="text"
                        placeholder="Enter your name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                        disabled={loading}
                        className="rounded-full border-2 py-6"
                      />
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value)
                        setError("")
                      }}
                      required
                      disabled={loading}
                      className="rounded-full border-2 py-6"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value)
                        setError("")
                      }}
                      required
                      disabled={loading}
                      className="rounded-full border-2 py-6"
                    />
                    {!isLogin && (
                      <p className="text-xs text-muted-foreground">Password must be at least 6 characters</p>
                    )}
                  </div>

                  {isLogin && (
                    <div className="flex justify-end">
                      <button
                        type="button"
                        onClick={() => {
                          setShowForgotPassword(true)
                          setError("")
                        }}
                        className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                      >
                        Forgot password?
                      </button>
                    </div>
                  )}

                  <Button
                    type="submit"
                    disabled={loading}
                    className="otome-glow group w-full gap-2 rounded-full bg-gradient-to-r from-purple-300/90 via-pink-200/80 to-blue-200/70 py-6 text-base text-foreground hover:from-purple-300 hover:via-pink-200 hover:to-blue-200 disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        {isLogin ? "Logging in..." : "Signing up..."}
                      </>
                    ) : (
                      <>
                        {isLogin ? "Log in" : "Sign up"}
                        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                      </>
                    )}
                  </Button>
                </form>

                {/* Toggle Login/Signup */}
                <div className="mt-6 text-center text-sm">
                  <span className="text-muted-foreground">
                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                  </span>
                  <button
                    onClick={() => {
                      setIsLogin(!isLogin)
                      setError("")
                    }}
                    disabled={loading}
                    className="font-semibold text-foreground hover:underline disabled:opacity-50"
                  >
                    {isLogin ? "Sign up" : "Log in"}
                  </button>
                </div>

                {!isLogin && (
                  <p className="mt-4 text-center text-xs text-muted-foreground">
                    By signing up, you agree to our Terms of Service and Privacy Policy
                  </p>
                )}
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
