"use client"

import { useState, useEffect } from "react"
import { Calendar, Clock, ChevronLeft, ChevronRight, Plus, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/hooks/use-auth"
import {
  checkGoogleAuthStatus,
  initiateGoogleAuth,
  getCalendarEvents,
  getUserCalendars,
  CalendarEvent,
  CalendarInfo,
  CalendarEventsResponse,
  CalendarAuthStatus
} from "@/lib/api"

interface CalendarPageProps {
  isOpen: boolean
  onClose: () => void
}

export function CalendarPage({ isOpen, onClose }: CalendarPageProps) {
  const { user } = useAuth()
  const [authStatus, setAuthStatus] = useState<CalendarAuthStatus | null>(null)
  const [calendars, setCalendars] = useState<CalendarInfo[]>([])
  const [selectedCalendar, setSelectedCalendar] = useState<string>("primary")
  const [events, setEvents] = useState<CalendarEventsResponse | null>(null)
  const [currentDate, setCurrentDate] = useState(new Date())
  const [isLoading, setIsLoading] = useState(false)
  const [isAuthenticating, setIsAuthenticating] = useState(false)

  // Check authentication status on mount
  useEffect(() => {
    if (isOpen && user) {
      checkAuth()
    }
  }, [isOpen, user])

  // Load calendars and events when authenticated
  useEffect(() => {
    if (authStatus?.authenticated && user) {
      loadCalendars()
      loadEvents()
    }
  }, [authStatus?.authenticated, user, selectedCalendar])

  const checkAuth = async () => {
    if (!user) return

    try {
      const status = await checkGoogleAuthStatus(user.uid)
      setAuthStatus(status)
    } catch (error) {
      console.error("Failed to check auth status:", error)
      setAuthStatus({ authenticated: false, error: "Failed to check authentication" })
    }
  }

  const handleGoogleAuth = async () => {
    if (!user) return

    setIsAuthenticating(true)
    try {
      const authResponse = await initiateGoogleAuth(user.uid)
      // Redirect to Google OAuth
      window.location.href = authResponse.auth_url
    } catch (error) {
      console.error("Failed to initiate auth:", error)
      setIsAuthenticating(false)
    }
  }

  const loadCalendars = async () => {
    if (!user) return

    try {
      const userCalendars = await getUserCalendars(user.uid)
      setCalendars(userCalendars)
    } catch (error) {
      console.error("Failed to load calendars:", error)
    }
  }

  const loadEvents = async () => {
    if (!user) return

    setIsLoading(true)
    try {
      const eventsData = await getCalendarEvents(user.uid, selectedCalendar, 50, 30)
      setEvents(eventsData)
    } catch (error) {
      console.error("Failed to load events:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatEventTime = (event: CalendarEvent) => {
    const start = event.start.dateTime || event.start.date
    if (!start) return ""

    const date = new Date(start)
    const now = new Date()
    const isToday = date.toDateString() === now.toDateString()
    const isTomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000).toDateString() === date.toDateString()

    let dateStr = ""
    if (isToday) {
      dateStr = "Today"
    } else if (isTomorrow) {
      dateStr = "Tomorrow"
    } else {
      dateStr = date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
    }

    if (event.start.dateTime) {
      // Has time
      const timeStr = date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      })
      return `${dateStr} at ${timeStr}`
    } else {
      // All-day event
      return dateStr
    }
  }

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev)
      if (direction === 'prev') {
        newDate.setMonth(newDate.getMonth() - 1)
      } else {
        newDate.setMonth(newDate.getMonth() + 1)
      }
      return newDate
    })
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />

      {/* Modal */}
      <div className="relative z-10 w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-3xl bg-background shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-green-300/80 via-blue-200/70 to-purple-200/60">
              <Calendar className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Your Calendar</h2>
              <p className="text-sm text-muted-foreground">Sync with Google Calendar for outfit recommendations</p>
            </div>
          </div>
          <button onClick={onClose} className="rounded-full p-2 hover:bg-secondary">
            <ChevronLeft className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[calc(90vh-140px)] overflow-y-auto">
          {!user ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Calendar className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Please Log In</h3>
              <p className="text-muted-foreground text-center">You need to be logged in to access your calendar.</p>
            </div>
          ) : !authStatus?.authenticated ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Calendar className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Connect Google Calendar</h3>
              <p className="text-muted-foreground text-center mb-6">
                Sync your calendar to get personalized outfit recommendations based on your upcoming events.
              </p>
              <Button
                onClick={handleGoogleAuth}
                disabled={isAuthenticating}
                className="rounded-full px-8"
              >
                {isAuthenticating ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <Calendar className="mr-2 h-4 w-4" />
                    Connect Google Calendar
                  </>
                )}
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Auth Status */}
              <div className="flex items-center justify-between p-4 bg-secondary/50 rounded-xl">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center">
                    <Calendar className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <p className="font-medium">Connected to Google Calendar</p>
                    <p className="text-sm text-muted-foreground">{authStatus.email}</p>
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={loadEvents}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>

              {/* Calendar Selector */}
              {calendars.length > 1 && (
                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium">Calendar:</label>
                  <select
                    value={selectedCalendar}
                    onChange={(e) => setSelectedCalendar(e.target.value)}
                    className="rounded-lg border border-border bg-background px-3 py-1.5 text-sm"
                  >
                    {calendars.map((cal) => (
                      <option key={cal.id} value={cal.id}>
                        {cal.summary}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Upcoming Events */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Upcoming Events</h3>

                {isLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
                    <span className="ml-2 text-muted-foreground">Loading events...</span>
                  </div>
                ) : events?.events.length === 0 ? (
                  <div className="text-center py-8">
                    <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No upcoming events found.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {events?.events.map((event) => (
                      <div key={event.id} className="flex items-center gap-4 p-4 border rounded-xl hover:bg-secondary/50 transition-colors">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                          <Calendar className="h-5 w-5 text-primary" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium">{event.summary}</h4>
                          <p className="text-sm text-muted-foreground">{formatEventTime(event)}</p>
                          {event.location && (
                            <p className="text-xs text-muted-foreground">{event.location}</p>
                          )}
                        </div>
                        {event.htmlLink && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(event.htmlLink, '_blank')}
                          >
                            View
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Occasions Analysis */}
              {events?.occasions && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Outfit Recommendations</h3>
                  <div className="p-4 bg-secondary/30 rounded-xl">
                    <p className="text-sm">{events.occasions.total_events} upcoming events</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {Object.entries(events.occasions.by_type)
                        .filter(([_, events]) => events.length > 0)
                        .map(([type, typeEvents]) => (
                          <span key={type} className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full">
                            {typeEvents.length} {type}
                          </span>
                        ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}