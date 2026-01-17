import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  User,
  sendPasswordResetEmail,
  updateProfile,
} from 'firebase/auth'
import { doc, setDoc, getDoc, serverTimestamp } from 'firebase/firestore'
import { auth, db } from './firebase'

// Google OAuth provider
const googleProvider = new GoogleAuthProvider()
googleProvider.setCustomParameters({
  prompt: 'select_account',
})

/**
 * Sign up with email and password
 */
export async function signUpWithEmail(email: string, password: string, displayName?: string) {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password)
    const user = userCredential.user

    // Update display name if provided
    if (displayName) {
      await updateProfile(user, { displayName })
    }

    // Create user document in Firestore
    await createUserDocument(user, { displayName })

    return { user, error: null }
  } catch (error: any) {
    console.error('Sign up error:', error)
    return { user: null, error: getAuthErrorMessage(error) }
  }
}

/**
 * Sign in with email and password
 */
export async function signInWithEmail(email: string, password: string) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password)
    return { user: userCredential.user, error: null }
  } catch (error: any) {
    console.error('Sign in error:', error)
    return { user: null, error: getAuthErrorMessage(error) }
  }
}

/**
 * Sign in with Google OAuth
 */
export async function signInWithGoogle() {
  try {
    const result = await signInWithPopup(auth, googleProvider)
    const user = result.user

    // Check if user document exists, create if not
    const userDocRef = doc(db, 'users', user.uid)
    const userDoc = await getDoc(userDocRef)
    
    if (!userDoc.exists()) {
      await createUserDocument(user)
    }

    return { user, error: null, isNewUser: !userDoc.exists() }
  } catch (error: any) {
    console.error('Google sign in error:', error)
    return { user: null, error: getAuthErrorMessage(error), isNewUser: false }
  }
}

/**
 * Sign out current user
 */
export async function signOut() {
  try {
    await firebaseSignOut(auth)
    return { error: null }
  } catch (error: any) {
    console.error('Sign out error:', error)
    return { error: getAuthErrorMessage(error) }
  }
}

/**
 * Send password reset email
 */
export async function resetPassword(email: string) {
  try {
    await sendPasswordResetEmail(auth, email)
    return { error: null }
  } catch (error: any) {
    console.error('Password reset error:', error)
    return { error: getAuthErrorMessage(error) }
  }
}

/**
 * Listen to auth state changes
 */
export function onAuthChange(callback: (user: User | null) => void) {
  return onAuthStateChanged(auth, callback)
}

/**
 * Create user document in Firestore
 */
async function createUserDocument(user: User, additionalData?: any) {
  const userDocRef = doc(db, 'users', user.uid)
  
  const userData = {
    uid: user.uid,
    email: user.email,
    displayName: additionalData?.displayName || user.displayName || '',
    photoURL: user.photoURL || '',
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
    // Additional user profile fields
    firstName: '',
    lastName: '',
    username: '',
    location: null,
    gender: null,
    bodySize: {},
    preferences: {},
    onboardingCompleted: false,
  }

  await setDoc(userDocRef, userData, { merge: true })
  return userData
}

/**
 * Get current user
 */
export function getCurrentUser(): User | null {
  return auth.currentUser
}

/**
 * Convert Firebase error codes to user-friendly messages
 */
function getAuthErrorMessage(error: any): string {
  const errorCode = error.code
  
  switch (errorCode) {
    case 'auth/email-already-in-use':
      return 'This email is already registered. Please sign in instead.'
    case 'auth/invalid-email':
      return 'Invalid email address.'
    case 'auth/operation-not-allowed':
      return 'This sign-in method is not enabled. Please contact support.'
    case 'auth/weak-password':
      return 'Password should be at least 6 characters.'
    case 'auth/user-disabled':
      return 'This account has been disabled.'
    case 'auth/user-not-found':
      return 'No account found with this email.'
    case 'auth/wrong-password':
      return 'Incorrect password.'
    case 'auth/popup-closed-by-user':
      return 'Sign in was cancelled.'
    case 'auth/cancelled-popup-request':
      return 'Only one popup request is allowed at a time.'
    case 'auth/popup-blocked':
      return 'Sign in popup was blocked by the browser.'
    case 'auth/network-request-failed':
      return 'Network error. Please check your internet connection.'
    case 'auth/too-many-requests':
      return 'Too many attempts. Please try again later.'
    default:
      return error.message || 'An error occurred. Please try again.'
  }
}
