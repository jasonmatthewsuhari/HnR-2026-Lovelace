"""
Firebase Configuration Helper Script

This script helps you set up Firebase with Google Authentication for Lovelace.
It will guide you through getting your credentials and testing the connection.
"""

import os
import sys
import json
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_step(step_num, text):
    """Print a formatted step"""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {text}")
    print('='*70 + "\n")


def get_firebase_service_account():
    """Guide user to get Firebase service account credentials"""
    print_step(1, "Get Firebase Service Account Credentials")
    
    print("📝 Follow these steps in Firebase Console:")
    print()
    print("1. Go to: https://console.firebase.google.com/")
    print("2. Select your project")
    print("3. Click the ⚙️ (gear icon) next to 'Project Overview'")
    print("4. Select 'Project settings'")
    print("5. Go to the 'Service accounts' tab")
    print("6. Click 'Generate new private key'")
    print("7. Click 'Generate key' in the dialog")
    print("8. Save the downloaded JSON file")
    print()
    
    input("Press Enter once you've downloaded the service account JSON file...")
    
    while True:
        file_path = input("\nEnter the full path to your service account JSON file: ").strip().strip('"')
        
        if os.path.exists(file_path):
            print(f"\n✓ Found file: {file_path}")
            return file_path
        else:
            print(f"\n❌ File not found: {file_path}")
            retry = input("Try again? (y/n): ")
            if retry.lower() != 'y':
                return None


def get_firebase_web_config():
    """Guide user to get Firebase web app configuration"""
    print_step(2, "Get Firebase Web App Configuration")
    
    print("📝 Follow these steps in Firebase Console:")
    print()
    print("1. Go to: https://console.firebase.google.com/")
    print("2. Select your project")
    print("3. Click the ⚙️ (gear icon) next to 'Project Overview'")
    print("4. Select 'Project settings'")
    print("5. Scroll down to 'Your apps'")
    print("6. If you haven't added a web app yet:")
    print("   - Click the '</>' (web) icon")
    print("   - Register your app with a nickname (e.g., 'Lovelace Web')")
    print("7. You'll see a config object like this:")
    print()
    print("   const firebaseConfig = {")
    print("     apiKey: 'AIza...',")
    print("     authDomain: 'your-project.firebaseapp.com',")
    print("     projectId: 'your-project-id',")
    print("     storageBucket: 'your-project.appspot.com',")
    print("     messagingSenderId: '123456789',")
    print("     appId: '1:123:web:abc123'")
    print("   };")
    print()
    
    print("Copy the values from your Firebase config:")
    print()
    
    config = {}
    config['apiKey'] = input("apiKey: ").strip()
    config['authDomain'] = input("authDomain: ").strip()
    config['projectId'] = input("projectId: ").strip()
    config['storageBucket'] = input("storageBucket: ").strip()
    config['messagingSenderId'] = input("messagingSenderId: ").strip()
    config['appId'] = input("appId: ").strip()
    
    return config


def setup_environment_file(service_account_path, web_config):
    """Create or update .env file with Firebase configuration"""
    print_step(3, "Setting Up Environment Variables")
    
    backend_dir = Path(__file__).parent
    env_file = backend_dir / '.env'
    
    # Copy service account file to backend directory
    dest_path = backend_dir / 'firebase-credentials.json'
    
    print(f"\nCopying service account file to: {dest_path}")
    
    import shutil
    try:
        shutil.copy2(service_account_path, dest_path)
        print("✓ Service account file copied")
    except Exception as e:
        print(f"❌ Error copying file: {e}")
        return False
    
    # Create .env file
    env_content = f"""# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID={web_config['projectId']}
FIREBASE_STORAGE_BUCKET={web_config['storageBucket']}
FIREBASE_API_KEY={web_config['apiKey']}
FIREBASE_AUTH_DOMAIN={web_config['authDomain']}
FIREBASE_APP_ID={web_config['appId']}

# Environment
ENVIRONMENT=development
DEBUG=True

# Server Configuration
HOST=0.0.0.0
PORT=8000

# JWT Configuration (generate a secure key for production)
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Feature Flags
ENABLE_GOOGLE_AUTH=true
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"\n✓ Created .env file: {env_file}")
        return True
    except Exception as e:
        print(f"\n❌ Error creating .env file: {e}")
        return False


def create_frontend_config(web_config):
    """Create Firebase configuration file for frontend"""
    print_step(4, "Creating Frontend Configuration")
    
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    config_dir = frontend_dir / 'lib'
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / 'firebase-config.ts'
    
    config_content = f"""// Firebase Configuration for Lovelace Frontend
// Auto-generated by setup script

import {{ initializeApp }} from 'firebase/app';
import {{ getAuth, GoogleAuthProvider }} from 'firebase/auth';
import {{ getFirestore }} from 'firebase/firestore';
import {{ getStorage }} from 'firebase/storage';

const firebaseConfig = {{
  apiKey: "{web_config['apiKey']}",
  authDomain: "{web_config['authDomain']}",
  projectId: "{web_config['projectId']}",
  storageBucket: "{web_config['storageBucket']}",
  messagingSenderId: "{web_config['messagingSenderId']}",
  appId: "{web_config['appId']}"
}};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

// Google Auth Provider
export const googleProvider = new GoogleAuthProvider();

export default app;
"""
    
    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        print(f"✓ Created frontend config: {config_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating frontend config: {e}")
        return False


def test_firebase_connection():
    """Test the Firebase connection"""
    print_step(5, "Testing Firebase Connection")
    
    print("Testing Firebase Admin SDK connection...")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        # Check if already initialized
        try:
            firebase_admin.get_app()
            print("✓ Firebase already initialized")
        except ValueError:
            cred = credentials.Certificate('./firebase-credentials.json')
            firebase_admin.initialize_app(cred)
            print("✓ Firebase initialized successfully")
        
        # Test Firestore connection
        db = firestore.client()
        print("✓ Connected to Firestore")
        
        # Try to write a test document
        test_ref = db.collection('_test').document('connection_test')
        test_ref.set({
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'Firebase connection test successful!'
        })
        print("✓ Successfully wrote test document")
        
        # Clean up test document
        test_ref.delete()
        print("✓ Cleaned up test document")
        
        return True
        
    except ImportError:
        print("\n❌ Firebase Admin SDK not installed!")
        print("Run: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"\n❌ Error testing Firebase: {e}")
        return False


def setup_firestore_rules():
    """Guide user to set up Firestore security rules"""
    print_step(6, "Set Up Firestore Security Rules")
    
    print("📝 Set up security rules in Firebase Console:")
    print()
    print("1. Go to: https://console.firebase.google.com/")
    print("2. Select your project")
    print("3. Go to 'Firestore Database' in the left menu")
    print("4. Click on the 'Rules' tab")
    print("5. Replace the rules with the following:")
    print()
    print("=" * 70)
    print("""
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper function to check if user is authenticated
    function isAuthenticated() {
      return request.auth != null;
    }
    
    // Helper function to check if user owns the document
    function isOwner(userId) {
      return isAuthenticated() && request.auth.uid == userId;
    }
    
    // Users collection
    match /users/{userId} {
      allow read: if isAuthenticated();
      allow write: if isOwner(userId);
    }
    
    // Clothing items collection
    match /clothing_items/{itemId} {
      allow read: if isAuthenticated();
      allow create: if isAuthenticated();
      allow update, delete: if isAuthenticated() && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Outfits collection
    match /outfits/{outfitId} {
      allow read: if isAuthenticated();
      allow create: if isAuthenticated();
      allow update, delete: if isAuthenticated() && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Collections
    match /collections/{collectionId} {
      allow read: if isAuthenticated();
      allow create: if isAuthenticated();
      allow update, delete: if isAuthenticated() && 
        resource.data.user_id == request.auth.uid;
    }
  }
}
""")
    print("=" * 70)
    print()
    print("6. Click 'Publish' to apply the rules")
    print()
    
    input("Press Enter once you've set up the security rules...")


def main():
    """Main setup flow"""
    print_header("🔥 FIREBASE SETUP FOR LOVELACE")
    
    print("This script will help you configure Firebase for Lovelace.")
    print("You'll need:")
    print("  ✓ A Firebase project (which you've already created)")
    print("  ✓ Google Sign-In enabled (which you've already done)")
    print()
    
    input("Press Enter to continue...")
    
    # Step 1: Get service account credentials
    service_account_path = get_firebase_service_account()
    if not service_account_path:
        print("\n❌ Setup cancelled. Please get the service account file first.")
        return
    
    # Step 2: Get web app configuration
    web_config = get_firebase_web_config()
    
    # Step 3: Setup environment file
    if not setup_environment_file(service_account_path, web_config):
        print("\n❌ Failed to set up environment file")
        return
    
    # Step 4: Create frontend configuration
    create_frontend_config(web_config)
    
    # Step 5: Test connection
    if test_firebase_connection():
        print("\n✓ Firebase connection successful!")
    else:
        print("\n⚠️  Connection test failed, but configuration files were created.")
        print("You may need to install dependencies: pip install firebase-admin")
    
    # Step 6: Set up Firestore rules
    setup_firestore_rules()
    
    # Final instructions
    print_header("🎉 SETUP COMPLETE!")
    
    print("✓ Firebase service account configured")
    print("✓ Environment variables created (.env)")
    print("✓ Frontend configuration created")
    print("✓ Security rules instructions provided")
    print()
    print("Next steps:")
    print()
    print("1. Install Python dependencies:")
    print("   cd backend")
    print("   pip install -r requirements.txt")
    print()
    print("2. Install frontend dependencies:")
    print("   cd frontend")
    print("   npm install firebase")
    print()
    print("3. Start the backend server:")
    print("   cd backend")
    print("   python main.py")
    print()
    print("4. Start the frontend:")
    print("   cd frontend")
    print("   npm run dev")
    print()
    print("5. Test Google Sign-In at: http://localhost:3000")
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
