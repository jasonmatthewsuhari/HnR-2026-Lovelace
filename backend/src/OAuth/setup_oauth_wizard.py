"""
Interactive OAuth Setup Wizard
Guides you through setting up Google OAuth for Calendar integration
"""

import os
import sys
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_step(number, text):
    """Print a step number and description"""
    print(f"\n{'='*70}")
    print(f"STEP {number}: {text}")
    print(f"{'='*70}\n")

def wait_for_enter(message="Press ENTER to continue..."):
    """Wait for user to press enter"""
    input(f"\n{message}")

def main():
    """Main setup wizard"""
    
    print("\n" + "🎨"*35)
    print("\n     🚀 LOVELACE - GOOGLE OAUTH SETUP WIZARD 🚀\n")
    print("🎨"*35 + "\n")
    
    print("This wizard will help you set up Google Calendar OAuth integration.")
    print("The process takes about 5-10 minutes.\n")
    
    wait_for_enter("Ready to start? Press ENTER...")
    
    # ========================================================================
    # STEP 1: Check if .env exists
    # ========================================================================
    
    print_step(1, "Check Environment File")
    
    # Navigate to project root (3 levels up from OAuth folder)
    # backend/src/OAuth -> backend/src -> backend -> project root
    project_root = Path(__file__).parent.parent.parent.parent
    env_path = project_root / ".env"
    env_example_path = project_root / "backend" / "env.example"
    
    print(f"Looking for .env at: {env_path.absolute()}")
    print(f"(This should be at project root, same level as README.md)")
    
    if env_path.exists():
        print(f"✅ Found existing .env file at project root")
        overwrite = input("\n⚠️  Do you want to add/update OAuth configuration? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("\n❌ Setup cancelled. Your existing .env file was not modified.")
            sys.exit(0)
    else:
        print(f"ℹ️  No .env file found at project root. We'll create one.")
        
        if env_example_path.exists():
            print(f"📋 Found env.example at: {env_example_path}")
            copy_example = input("\n   Copy from backend/env.example as template? (y/n): ").strip().lower()
            if copy_example == 'y':
                import shutil
                shutil.copy(env_example_path, env_path)
                print(f"✅ Created .env at project root from backend/env.example")
        else:
            env_path.touch()
            print(f"✅ Created empty .env file at project root")
    
    # ========================================================================
    # STEP 2: Get OAuth Credentials from Google Cloud
    # ========================================================================
    
    print_step(2, "Get OAuth Credentials from Google Cloud Console")
    
    print("You need to create OAuth credentials in Google Cloud Console.")
    print("\n📋 Instructions:")
    print("   1. Open: https://console.cloud.google.com/apis/credentials")
    print("   2. Select your project (or create a new one)")
    print("   3. Click 'CREATE CREDENTIALS' → 'OAuth client ID'")
    print("   4. If prompted, configure OAuth consent screen first")
    print("   5. Application type: Choose 'Web application'")
    print("   6. Name: 'Lovelace OAuth Client'")
    print("   7. Authorized redirect URIs - Click 'ADD URI' and add:")
    print("      http://localhost:3000/calendar/auth/callback")
    print("   8. Click 'CREATE'")
    print("   9. Copy the Client ID and Client Secret")
    
    wait_for_enter("\nComplete the above steps, then press ENTER...")
    
    # Get Client ID
    print("\n" + "-"*70)
    print("Enter your OAuth Client ID:")
    print("(Should look like: 123456789-abc...xyz.apps.googleusercontent.com)")
    print("-"*70)
    
    while True:
        client_id = input("\nOAuth Client ID: ").strip()
        if not client_id:
            print("❌ Client ID cannot be empty!")
            continue
        if len(client_id) < 20:
            print("⚠️  That seems too short for a Client ID. Are you sure? (y/n)")
            confirm = input().strip().lower()
            if confirm != 'y':
                continue
        break
    
    print(f"✅ Client ID: {client_id[:30]}...")
    
    # Get Client Secret
    print("\n" + "-"*70)
    print("Enter your OAuth Client Secret:")
    print("(Should look like: GOCSPX-abc...xyz)")
    print("-"*70)
    
    while True:
        client_secret = input("\nOAuth Client Secret: ").strip()
        if not client_secret:
            print("❌ Client Secret cannot be empty!")
            continue
        if len(client_secret) < 10:
            print("⚠️  That seems too short for a Client Secret. Are you sure? (y/n)")
            confirm = input().strip().lower()
            if confirm != 'y':
                continue
        break
    
    masked_secret = client_secret[:4] + "*"*(len(client_secret)-8) + client_secret[-4:]
    print(f"✅ Client Secret: {masked_secret}")
    
    # Redirect URI
    redirect_uri = "http://localhost:3000/calendar/auth/callback"
    print(f"\n✅ Redirect URI will be set to: {redirect_uri}")
    
    # ========================================================================
    # STEP 3: Save to .env file
    # ========================================================================
    
    print_step(3, "Save Configuration")
    
    # Read existing .env file
    env_lines = []
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_lines = f.readlines()
    
    # Remove existing OAuth lines
    env_lines = [line for line in env_lines 
                 if not any(key in line for key in ['OAUTH_CLIENT_ID', 'OAUTH_CLIENT_SECRET', 'OAUTH_REDIRECT_URI'])]
    
    # Find where to insert OAuth config (after Firebase or at end)
    insert_index = len(env_lines)
    for i, line in enumerate(env_lines):
        if '=== Google OAuth Configuration ===' in line:
            insert_index = i
            break
        elif '=== Server Configuration ===' in line:
            insert_index = i
            break
    
    # Prepare OAuth configuration
    oauth_config = [
        "\n",
        "# === Google OAuth Configuration (for Calendar Sync) ===\n",
        "# Get these from: https://console.cloud.google.com/apis/credentials\n",
        f"OAUTH_CLIENT_ID={client_id}\n",
        f"OAUTH_CLIENT_SECRET={client_secret}\n",
        f"OAUTH_REDIRECT_URI={redirect_uri}\n",
    ]
    
    # Insert OAuth config
    env_lines[insert_index:insert_index] = oauth_config
    
    # Write back to file
    with open(env_path, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ Configuration saved to: {env_path.absolute()}")
    print(f"   (At project root, same level as README.md)")
    
    # ========================================================================
    # STEP 4: Enable Google Calendar API
    # ========================================================================
    
    print_step(4, "Enable Google Calendar API")
    
    print("You need to enable the Google Calendar API for your project.")
    print("\n📋 Instructions:")
    print("   1. Open: https://console.cloud.google.com/apis/library")
    print("   2. Search for 'Google Calendar API'")
    print("   3. Click on it")
    print("   4. Click 'ENABLE'")
    print("   5. Wait for it to enable (takes a few seconds)")
    
    wait_for_enter("\nComplete the above steps, then press ENTER...")
    
    # ========================================================================
    # STEP 5: Verify Configuration
    # ========================================================================
    
    print_step(5, "Verify Configuration")
    
    print("Let's verify your configuration is correct...")
    print("\nLoading .env file...")
    
    # Load the .env file
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        # Check if values are loaded
        loaded_client_id = os.getenv('OAUTH_CLIENT_ID')
        loaded_client_secret = os.getenv('OAUTH_CLIENT_SECRET')
        loaded_redirect_uri = os.getenv('OAUTH_REDIRECT_URI')
        
        if loaded_client_id == client_id:
            print("✅ OAUTH_CLIENT_ID loaded correctly")
        else:
            print("⚠️  OAUTH_CLIENT_ID mismatch (may need to restart server)")
        
        if loaded_client_secret == client_secret:
            print("✅ OAUTH_CLIENT_SECRET loaded correctly")
        else:
            print("⚠️  OAUTH_CLIENT_SECRET mismatch (may need to restart server)")
        
        if loaded_redirect_uri == redirect_uri:
            print("✅ OAUTH_REDIRECT_URI loaded correctly")
        else:
            print(f"ℹ️  OAUTH_REDIRECT_URI will use: {redirect_uri}")
        
    except Exception as e:
        print(f"⚠️  Could not verify configuration: {e}")
        print("   This is okay - just restart your server after setup")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print_header("🎉 SETUP COMPLETE!")
    
    print("Your Google OAuth configuration is ready!")
    print("\n📋 Configuration Summary:")
    print(f"   • Client ID: {client_id[:30]}...")
    print(f"   • Client Secret: {masked_secret}")
    print(f"   • Redirect URI: {redirect_uri}")
    print(f"   • Config file: {env_path.absolute()}")
    print(f"   • Location: Project root (same level as README.md)")
    
    print("\n" + "="*70)
    print("🚀 NEXT STEPS")
    print("="*70)
    
    print("\n1. ⏱️  WAIT 1-2 minutes for Google Cloud changes to propagate")
    
    print("\n2. 🔄 RESTART your backend server:")
    print("   cd backend")
    print("   uvicorn main:app --reload --port 8000")
    
    print("\n3. 🌐 START your frontend (if not running):")
    print("   cd frontend")
    print("   npm run dev")
    
    print("\n4. 🧪 TEST the integration:")
    print("   • Open: http://localhost:3000")
    print("   • Log into Lovelace")
    print("   • Navigate to Calendar page")
    print("   • Click 'Connect to Google Calendar'")
    print("   • Authorize access")
    print("   • Should work! ✨")
    
    print("\n" + "="*70)
    print("📚 DOCUMENTATION")
    print("="*70)
    
    print("\n   • Quick Reference: backend/src/OAuth/QUICKFIX.md")
    print("   • Detailed Guide: backend/src/OAuth/REDIRECT_URI_FIX.md")
    print("   • Full OAuth Docs: backend/src/OAuth/README.MD")
    print("   • Config Checker: python backend/src/OAuth/check_oauth_config.py")
    
    print("\n" + "="*70)
    print("🆘 TROUBLESHOOTING")
    print("="*70)
    
    print("\n   • Run config checker: python check_oauth_config.py")
    print("   • Check redirect URI matches EXACTLY in Google Cloud Console")
    print("   • Make sure Google Calendar API is enabled")
    print("   • Clear browser cache or use incognito window")
    print("   • Wait 1-2 minutes after Google Cloud Console changes")
    
    print("\n" + "🎨"*35)
    print("\n     ✨ Happy coding with Lovelace! ✨\n")
    print("🎨"*35 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
