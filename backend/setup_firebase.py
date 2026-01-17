"""
Firebase Setup Helper Script

This script helps you set up Firebase for the Lovelace Wardrobe Database.
"""

import os
import sys


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")


def print_step(step_num, text):
    """Print a formatted step"""
    print(f"\n{step_num}. {text}")
    print("-" * 60)


def main():
    print_header("Lovelace Firebase Setup Helper")
    
    print("This script will guide you through setting up Firebase for Lovelace.")
    print("\nPrerequisites:")
    print("  ✓ Python 3.7 or higher")
    print("  ✓ pip installed")
    print("  ✓ Firebase account")
    
    # Step 1: Install dependencies
    print_step(1, "Install Firebase Admin SDK")
    print("\nRun the following command to install dependencies:")
    print("\n  pip install -r requirements.txt")
    print("\nOr install just Firebase:")
    print("\n  pip install firebase-admin")
    
    response = input("\nHave you installed the dependencies? (y/n): ")
    if response.lower() != 'y':
        print("\nPlease install dependencies first, then run this script again.")
        return
    
    # Step 2: Firebase Console Setup
    print_step(2, "Set up Firebase Project")
    print("\n1. Go to https://console.firebase.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Click on the gear icon (⚙️) > Project Settings")
    print("4. Navigate to the 'Service Accounts' tab")
    print("5. Click 'Generate New Private Key'")
    print("6. Save the downloaded JSON file securely")
    
    response = input("\nHave you downloaded the Firebase credentials JSON file? (y/n): ")
    if response.lower() != 'y':
        print("\nPlease download the credentials file first.")
        return
    
    # Step 3: Configure credentials
    print_step(3, "Configure Credentials")
    
    creds_path = input("\nEnter the full path to your Firebase credentials JSON file: ").strip()
    
    if not os.path.exists(creds_path):
        print(f"\n❌ File not found: {creds_path}")
        print("\nPlease check the path and try again.")
        return
    
    print(f"\n✓ Found credentials file: {creds_path}")
    
    # Suggest moving to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    suggested_path = os.path.join(backend_dir, "firebase-credentials.json")
    
    print(f"\nRecommendation: Move the file to: {suggested_path}")
    print("(This keeps credentials with your backend code)")
    
    move_file = input("\nWould you like to copy the file there? (y/n): ")
    
    if move_file.lower() == 'y':
        import shutil
        try:
            shutil.copy2(creds_path, suggested_path)
            print(f"\n✓ Credentials copied to: {suggested_path}")
            creds_path = suggested_path
        except Exception as e:
            print(f"\n❌ Error copying file: {e}")
            print("You can manually copy it later.")
    
    # Step 4: Set environment variable
    print_step(4, "Set Environment Variable")
    
    print("\nYou need to set the FIREBASE_CREDENTIALS_PATH environment variable.")
    print("\nFor Windows (Command Prompt):")
    print(f"  set FIREBASE_CREDENTIALS_PATH={creds_path}")
    print("\nFor Windows (PowerShell):")
    print(f"  $env:FIREBASE_CREDENTIALS_PATH=\"{creds_path}\"")
    print("\nFor Linux/Mac (bash/zsh):")
    print(f"  export FIREBASE_CREDENTIALS_PATH={creds_path}")
    
    print("\nTo make it permanent, add this to your:")
    print("  - Windows: System Environment Variables")
    print("  - Linux/Mac: ~/.bashrc or ~/.zshrc")
    
    # Step 5: Create .env file
    print_step(5, "Create .env File (Optional)")
    
    create_env = input("\nWould you like to create a .env file? (y/n): ")
    
    if create_env.lower() == 'y':
        env_path = os.path.join(backend_dir, ".env")
        env_content = f"FIREBASE_CREDENTIALS_PATH={creds_path}\nENVIRONMENT=development\n"
        
        try:
            with open(env_path, 'w') as f:
                f.write(env_content)
            print(f"\n✓ Created .env file: {env_path}")
            print("\nNote: Install python-dotenv to use .env files:")
            print("  pip install python-dotenv")
        except Exception as e:
            print(f"\n❌ Error creating .env file: {e}")
    
    # Step 6: Test connection
    print_step(6, "Test Firebase Connection")
    
    test_now = input("\nWould you like to test the connection now? (y/n): ")
    
    if test_now.lower() == 'y':
        print("\nTesting Firebase connection...")
        print(f"Setting FIREBASE_CREDENTIALS_PATH={creds_path}")
        os.environ['FIREBASE_CREDENTIALS_PATH'] = creds_path
        
        try:
            sys.path.insert(0, os.path.join(backend_dir, 'src', 'WardrobeDB'))
            from wardrobe_db import WardrobeDB
            
            db = WardrobeDB(credentials_path=creds_path)
            print("\n✓ Successfully connected to Firebase!")
            
        except Exception as e:
            print(f"\n❌ Connection failed: {e}")
            print("\nTroubleshooting:")
            print("  1. Check that the credentials file is valid")
            print("  2. Ensure Firebase Admin SDK is installed")
            print("  3. Check your internet connection")
            return
    
    # Final summary
    print_header("Setup Complete! 🎉")
    
    print("Next steps:")
    print("\n1. Run the wardrobe database script:")
    print("   cd backend/src/WardrobeDB")
    print("   python wardrobe_db.py")
    print("\n2. Read the documentation:")
    print("   backend/src/WardrobeDB/README.md")
    print("\n3. Set up Firestore security rules in Firebase Console")
    print("\n4. Integrate with your frontend application")
    
    print("\n" + "=" * 60)
    print("Happy coding! 💻✨")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
