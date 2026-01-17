"""
Firebase Web App Configuration Helper

This script helps you get the Firebase configuration for your web app.
Run this to get the values you need for your .env.local file.
"""

import json
import os

def main():
    print("=" * 60)
    print("Firebase Web App Configuration Helper")
    print("=" * 60)
    print()
    
    # Try to read existing Firebase credentials
    cred_path = os.path.join(os.path.dirname(__file__), 'firebase-credentials.json')
    
    if os.path.exists(cred_path):
        with open(cred_path, 'r') as f:
            creds = json.load(f)
            project_id = creds.get('project_id')
            
        print(f"[OK] Found Firebase project: {project_id}")
        print()
        print("Next Steps:")
        print()
        print("1. Go to Firebase Console:")
        print(f"   https://console.firebase.google.com/project/{project_id}/settings/general")
        print()
        print("2. Scroll down to 'Your apps' section")
        print()
        print("3. If you don't see a Web app (</>), click 'Add app' and select Web")
        print("   - App nickname: Lovelace Web")
        print("   - No need to set up Firebase Hosting")
        print()
        print("4. Copy the firebaseConfig object and use these values in .env.local:")
        print()
        print("=" * 60)
        print("Your .env.local should look like this:")
        print("=" * 60)
        print()
        print(f"NEXT_PUBLIC_FIREBASE_API_KEY=<your-api-key>")
        print(f"NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN={project_id}.firebaseapp.com")
        print(f"NEXT_PUBLIC_FIREBASE_PROJECT_ID={project_id}")
        print(f"NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET={project_id}.appspot.com")
        print(f"NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=<your-sender-id>")
        print(f"NEXT_PUBLIC_FIREBASE_APP_ID=<your-app-id>")
        print()
        print("=" * 60)
        print()
        print("5. Enable Authentication Methods:")
        print(f"   https://console.firebase.google.com/project/{project_id}/authentication/providers")
        print()
        print("   [X] Enable Email/Password")
        print("   [X] Enable Google Sign-in")
        print()
        print("6. Install Firebase in frontend:")
        print("   cd frontend")
        print("   npm install firebase")
        print()
        print("7. Restart your Next.js dev server:")
        print("   npm run dev")
        print()
    else:
        print("[ERROR] firebase-credentials.json not found!")
        print()
        print("Please run setup_firebase.py first to set up Firebase.")
        print()

if __name__ == "__main__":
    main()
