/**
 * API Client for Lovelace Backend
 * 
 * Handles all API calls to the FastAPI backend with Firebase authentication
 */

import { auth } from './firebase'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Get the current user's ID token for authentication
 */
async function getAuthToken(): Promise<string | null> {
  const user = auth.currentUser
  if (!user) return null
  
  try {
    const token = await user.getIdToken()
    return token
  } catch (error) {
    console.error('Error getting auth token:', error)
    return null
  }
}

/**
 * Make an authenticated API request
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken()
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }
  
  return response.json()
}

// ==================== TYPES ====================

export interface ClothingItem {
  id: string
  user_id: string
  name: string
  category: string
  images: string[]
  color?: string
  size?: string
  brand?: string
  price?: string
  source?: string
  tags?: string[]
  created_at?: string
  updated_at?: string
}

export interface Outfit {
  id: string
  user_id: string
  name: string
  description?: string
  clothing_item_ids: string[]
  occasion?: string
  season?: string
  weather?: string
  liked?: boolean
  times_worn?: number
  last_worn?: string
  tags?: string[]
  created_at?: string
  updated_at?: string
}

export interface Collection {
  id: string
  user_id: string
  name: string
  description?: string
  outfit_ids: string[]
  is_wishlist?: boolean
  tags?: string[]
  created_at?: string
  updated_at?: string
}

export interface WardrobeStats {
  user_id: string
  total_clothing_items: number
  total_outfits: number
  total_collections: number
  category_breakdown: Record<string, number>
  estimated_wardrobe_value: string
  most_common_category?: string
}

// ==================== USER PROFILE ====================

export async function getUserProfile(userId: string) {
  return apiRequest<any>(`/api/users/${userId}`)
}

export async function updateUserProfile(userId: string, updates: any) {
  return apiRequest<any>(`/api/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  })
}

// ==================== CLOTHING ITEMS ====================

export async function addClothingItem(userId: string, item: Omit<ClothingItem, 'id' | 'user_id' | 'created_at' | 'updated_at'>) {
  return apiRequest<{ message: string; item_id: string; item: ClothingItem }>(
    `/api/users/${userId}/clothing`,
    {
      method: 'POST',
      body: JSON.stringify(item),
    }
  )
}

export async function getUserClothing(userId: string, category?: string) {
  const params = category ? `?category=${category}` : ''
  return apiRequest<{ items: ClothingItem[]; count: number }>(
    `/api/users/${userId}/clothing${params}`
  )
}

export async function getClothingItem(itemId: string) {
  return apiRequest<ClothingItem>(`/api/clothing/${itemId}`)
}

export async function updateClothingItem(itemId: string, updates: Partial<ClothingItem>) {
  return apiRequest<{ message: string; item_id: string }>(
    `/api/clothing/${itemId}`,
    {
      method: 'PUT',
      body: JSON.stringify(updates),
    }
  )
}

export async function deleteClothingItem(itemId: string) {
  return apiRequest<{ message: string; item_id: string }>(
    `/api/clothing/${itemId}`,
    {
      method: 'DELETE',
    }
  )
}

// ==================== OUTFITS ====================

export async function createOutfit(userId: string, outfit: Omit<Outfit, 'id' | 'user_id' | 'created_at' | 'updated_at' | 'liked' | 'times_worn' | 'last_worn'>) {
  return apiRequest<{ message: string; outfit_id: string; outfit: Outfit }>(
    `/api/users/${userId}/outfits`,
    {
      method: 'POST',
      body: JSON.stringify(outfit),
    }
  )
}

export async function getUserOutfits(userId: string, occasion?: string) {
  const params = occasion ? `?occasion=${occasion}` : ''
  return apiRequest<{ outfits: Outfit[]; count: number }>(
    `/api/users/${userId}/outfits${params}`
  )
}

export async function getOutfit(outfitId: string) {
  return apiRequest<{ outfit: Outfit; items: ClothingItem[] }>(
    `/api/outfits/${outfitId}`
  )
}

export async function updateOutfit(outfitId: string, updates: Partial<Outfit>) {
  return apiRequest<{ message: string; outfit_id: string }>(
    `/api/outfits/${outfitId}`,
    {
      method: 'PUT',
      body: JSON.stringify(updates),
    }
  )
}

export async function markOutfitWorn(outfitId: string) {
  return apiRequest<{ message: string; outfit_id: string }>(
    `/api/outfits/${outfitId}/worn`,
    {
      method: 'POST',
    }
  )
}

export async function deleteOutfit(outfitId: string) {
  return apiRequest<{ message: string; outfit_id: string }>(
    `/api/outfits/${outfitId}`,
    {
      method: 'DELETE',
    }
  )
}

// ==================== COLLECTIONS ====================

export async function createCollection(userId: string, collection: Omit<Collection, 'id' | 'user_id' | 'created_at' | 'updated_at'>) {
  return apiRequest<{ message: string; collection_id: string }>(
    `/api/users/${userId}/collections`,
    {
      method: 'POST',
      body: JSON.stringify(collection),
    }
  )
}

export async function getUserCollections(userId: string) {
  return apiRequest<{ collections: Collection[]; count: number }>(
    `/api/users/${userId}/collections`
  )
}

// ==================== STATISTICS ====================

export async function getWardrobeStats(userId: string) {
  return apiRequest<WardrobeStats>(`/api/users/${userId}/stats`)
}

// ==================== IMAGE PROCESSING ====================

export async function removeBackground(imageFile: File): Promise<string> {
  const token = await getAuthToken()

  const formData = new FormData()
  formData.append('image', imageFile)

  const headers: HeadersInit = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}/api/photobooth/remove-background`, {
    method: 'POST',
    headers,
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  const result = await response.json()
  return result.image // Returns base64 data URL
}

// ==================== GOOGLE CALENDAR ====================

export interface CalendarAuthStatus {
  authenticated: boolean
  email?: string
  name?: string
  error?: string
  message?: string
}

export interface CalendarEvent {
  id: string
  summary: string
  description?: string
  start: {
    dateTime?: string
    date?: string
    timeZone?: string
  }
  end: {
    dateTime?: string
    date?: string
    timeZone?: string
  }
  location?: string
  htmlLink?: string
}

export interface CalendarInfo {
  id: string
  summary: string
  description?: string
  primary?: boolean
  accessRole: string
}

export interface CalendarEventsResponse {
  events: CalendarEvent[]
  occasions: {
    total_events: number
    by_type: Record<string, any[]>
    special_occasions: any[]
  }
  calendar_id: string
  count: number
}

export interface OutfitContextResponse {
  context: string
  occasions: {
    total_events: number
    by_type: Record<string, any[]>
    special_occasions: any[]
  }
  analysis_period_days: number
}

export async function initiateGoogleAuth(userId: string): Promise<{ auth_url: string; message: string }> {
  return apiRequest('/api/calendar/auth/' + userId)
}

export async function exchangeGoogleAuthCode(userId: string, code: string): Promise<{ message: string; user_id: string }> {
  const params = new URLSearchParams({ code })
  return apiRequest(`/api/calendar/auth/exchange-code/${userId}?${params}`, {
    method: 'POST'
  })
}

export async function checkGoogleAuthStatus(userId: string): Promise<CalendarAuthStatus> {
  return apiRequest('/api/calendar/auth/status/' + userId)
}

export async function getUserCalendars(userId: string): Promise<CalendarInfo[]> {
  return apiRequest('/api/calendar/calendars/' + userId)
}

export async function getCalendarEvents(
  userId: string,
  calendarId: string = 'primary',
  maxResults: number = 10,
  daysAhead: number = 7
): Promise<CalendarEventsResponse> {
  const params = new URLSearchParams({
    calendar_id: calendarId,
    max_results: maxResults.toString(),
    days_ahead: daysAhead.toString()
  })
  return apiRequest(`/api/calendar/events/${userId}?${params}`)
}

export async function getEventsForDate(
  userId: string,
  date: string,
  calendarId: string = 'primary'
): Promise<CalendarEvent[]> {
  const params = new URLSearchParams({
    date,
    calendar_id: calendarId
  })
  return apiRequest(`/api/calendar/events/${userId}/date?${params}`)
}

export async function createCalendarEvent(
  userId: string,
  eventData: {
    summary: string
    start_time: string
    end_time: string
    description?: string
    location?: string
    calendar_id?: string
  }
): Promise<CalendarEvent> {
  return apiRequest(`/api/calendar/events/${userId}`, {
    method: 'POST',
    body: JSON.stringify(eventData),
  })
}

export async function getOutfitContext(userId: string, daysAhead: number = 7): Promise<OutfitContextResponse> {
  const params = new URLSearchParams({ days_ahead: daysAhead.toString() })
  return apiRequest(`/api/calendar/outfit-context/${userId}?${params}`)
}

export async function revokeGoogleAuth(userId: string): Promise<{ message: string; user_id: string }> {
  return apiRequest(`/api/calendar/auth/${userId}`, {
    method: 'DELETE',
  })
}