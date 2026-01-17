"""
Quick Firebase Connection Test

This script tests your Firebase setup and creates a .env file if needed.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with Firebase configuration"""
    backend_dir = Path(__file__).parent
    env_file = backend_dir / '.env'
    
    env_content = """# ============================================================================
# LOVELACE BACKEND - ENVIRONMENT VARIABLES
# ============================================================================

# Environment
ENVIRONMENT=development
DEBUG=True

# Server Configuration
HOST=0.0.0.0
PORT=8000

# ============================================================================
# FIREBASE / FIRESTORE
# ============================================================================
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=lovelace-b8ef5
FIREBASE_STORAGE_BUCKET=lovelace-b8ef5.appspot.com

# ============================================================================
# AUTHENTICATION & SECURITY
# ============================================================================
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# ============================================================================
# FEATURE FLAGS
# ============================================================================
ENABLE_GOOGLE_AUTH=true
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✓ Created .env file: {env_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def test_firebase_connection():
    """Test Firebase connection"""
    print("\n" + "=" * 70)
    print("  🔥 TESTING FIREBASE CONNECTION")
    print("=" * 70 + "\n")
    
    # Check if credentials file exists
    creds_file = Path(__file__).parent / 'firebase-credentials.json'
    if not creds_file.exists():
        print("❌ Firebase credentials file not found!")
        print(f"   Expected location: {creds_file}")
        return False
    
    print(f"✓ Found credentials file: {creds_file.name}")
    
    # Try to import Firebase Admin
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        print("✓ Firebase Admin SDK imported")
    except ImportError as e:
        print("\n❌ Firebase Admin SDK not installed!")
        print("Run: pip install firebase-admin")
        print(f"\nError: {e}")
        return False
    
    # Initialize Firebase
    try:
        # Check if already initialized
        try:
            app = firebase_admin.get_app()
            print("✓ Firebase already initialized")
        except ValueError:
            # Not initialized, so initialize now
            cred = credentials.Certificate(str(creds_file))
            app = firebase_admin.initialize_app(cred)
            print("✓ Firebase initialized successfully")
        
        # Test Firestore connection
        db = firestore.client()
        print("✓ Connected to Firestore")
        
        # Get project info
        print(f"\n📊 Project Information:")
        print(f"   Project ID: lovelace-b8ef5")
        print(f"   Database: Firestore")
        
        # Try to write a test document
        print("\n🧪 Testing write operation...")
        test_ref = db.collection('_connection_test').document('test')
        test_ref.set({
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'Connection test successful!',
            'status': 'working'
        })
        print("✓ Successfully wrote test document")
        
        # Read it back
        doc = test_ref.get()
        if doc.exists:
            print("✓ Successfully read test document")
            data = doc.to_dict()
            print(f"   Message: {data.get('message')}")
        
        # Clean up
        test_ref.delete()
        print("✓ Cleaned up test document")
        
        print("\n" + "=" * 70)
        print("  🎉 FIREBASE CONNECTION SUCCESSFUL!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Firebase connection failed!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("  🚀 LOVELACE FIREBASE QUICK TEST")
    print("=" * 70 + "\n")
    
    # Step 1: Create .env file
    print("Step 1: Setting up environment variables...")
    create_env_file()
    
    # Step 2: Test Firebase connection
    print("\nStep 2: Testing Firebase connection...")
    success = test_firebase_connection()
    
    if success:
        print("\n✅ Setup complete! Your Firebase is ready to use.")
        print("\nNext steps:")
        print("  1. Start the backend: python main.py")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Test the wardrobe database: cd src/WardrobeDB && python wardrobe_db.py")
    else:
        print("\n⚠️  Setup incomplete. Please check the errors above.")
        print("\nTroubleshooting:")
        print("  1. Make sure firebase-credentials.json is in the backend folder")
        print("  2. Install dependencies: pip install -r requirements.txt")
        print("  3. Check your internet connection")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
