import { useEffect, useState } from 'react'
import { User } from 'firebase/auth'
import { doc, getDoc } from 'firebase/firestore'
import { onAuthChange, signOut } from '@/lib/auth'
import { db } from '@/lib/firebase'

interface UserProfile {
  uid: string
  email: string | null
  displayName: string
  photoURL: string
  firstName?: string
  lastName?: string
  username?: string
  onboardingCompleted?: boolean
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthChange(async (firebaseUser) => {
      setUser(firebaseUser)
      
      if (firebaseUser) {
        // Fetch user profile from Firestore
        try {
          const userDocRef = doc(db, 'users', firebaseUser.uid)
          const userDoc = await getDoc(userDocRef)
          
          if (userDoc.exists()) {
            setUserProfile(userDoc.data() as UserProfile)
          }
        } catch (error) {
          console.error('Error fetching user profile:', error)
        }
      } else {
        setUserProfile(null)
      }
      
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  const logout = async () => {
    const { error } = await signOut()
    if (error) {
      throw new Error(error)
    }
    // Clear local storage on logout
    localStorage.removeItem('lovelace-user-profile')
  }

  return {
    user,
    userProfile,
    loading,
    isAuthenticated: !!user,
    logout,
  }
}
