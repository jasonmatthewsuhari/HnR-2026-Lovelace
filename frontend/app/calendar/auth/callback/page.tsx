"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Calendar, CheckCircle, XCircle, Loader2 } from "lucide-react"
import { exchangeGoogleAuthCode } from "@/lib/api"
import { useAuth } from "@/hooks/use-auth"

export default function CalendarAuthCallback() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user } = useAuth()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const error = searchParams.get('error')

      if (error) {
        setStatus('error')
        setMessage(`Authentication failed: ${error}`)
        return
      }

      if (!code) {
        setStatus('error')
        setMessage('No authorization code received')
        return
      }

      if (!user) {
        setStatus('error')
        setMessage('User not authenticated. Please log in first.')
        return
      }

      try {
        await exchangeGoogleAuthCode(user.uid, code)
        setStatus('success')
        setMessage('Successfully connected to Google Calendar!')

        // Redirect back to calendar page after a delay
        setTimeout(() => {
          router.push('/')
        }, 2000)
      } catch (error) {
        console.error('Failed to exchange code:', error)
        setStatus('error')
        setMessage('Failed to complete authentication. Please try again.')
      }
    }

    handleCallback()
  }, [searchParams, user, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="mb-6">
            <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-green-300/80 via-blue-200/70 to-purple-200/60">
              <Calendar className="h-8 w-8" />
            </div>
          </div>

          {status === 'loading' && (
            <>
              <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2">Connecting to Google Calendar</h2>
              <p className="text-muted-foreground">Please wait while we complete the authentication...</p>
            </>
          )}

          {status === 'success' && (
            <>
              <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2 text-green-700">Success!</h2>
              <p className="text-muted-foreground">{message}</p>
              <p className="text-sm text-muted-foreground mt-2">Redirecting you back...</p>
            </>
          )}

          {status === 'error' && (
            <>
              <XCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold mb-2 text-red-700">Authentication Failed</h2>
              <p className="text-muted-foreground">{message}</p>
              <button
                onClick={() => router.push('/')}
                className="mt-4 px-6 py-2 bg-primary text-primary-foreground rounded-full hover:bg-primary/90 transition-colors"
              >
                Go Back
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}