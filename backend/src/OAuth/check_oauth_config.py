"""
Quick OAuth Configuration Checker
Verifies that your OAuth setup is correct for Google Calendar integration
"""

import os
from pathlib import Path

# Try to load environment variables
try:
    from dotenv import load_dotenv
    # Load from project root
    project_root = Path(__file__).parent.parent.parent.parent
    env_path = project_root / ".env"
    load_dotenv(env_path)
    print("✅ dotenv library available")
except ImportError:
    print("⚠️  dotenv not installed - install with: pip install python-dotenv")

def check_oauth_config():
    """Check OAuth configuration and provide helpful feedback"""
    
    print("\n" + "="*70)
    print("🔍 OAUTH CONFIGURATION CHECKER")
    print("="*70 + "\n")
    
    # Check for .env file - it should be at project root
    # backend/src/OAuth -> backend/src -> backend -> project root
    project_root = Path(__file__).parent.parent.parent.parent
    env_path = project_root / ".env"
    
    print(f"Looking for .env at: {env_path.absolute()}")
    print(f"(Should be at project root, same level as README.md)\n")
    
    if env_path.exists():
        print(f"✅ .env file found at project root")
    else:
        print(f"❌ .env file NOT found at project root")
        print(f"   Expected location: {env_path.absolute()}")
        print(f"   → Create it: copy backend\\env.example .env")
        print(f"   → Location: Project root (same level as README.md)")
        return False
    
    # Check environment variables
    print("\n" + "-"*70)
    print("📋 Environment Variables Check:")
    print("-"*70)
    
    issues = []
    
    # Check OAUTH_CLIENT_ID
    client_id = os.getenv('OAUTH_CLIENT_ID')
    if client_id:
        if client_id.startswith('your_') or len(client_id) < 20:
            print("⚠️  OAUTH_CLIENT_ID: Set but looks like placeholder")
            print(f"   Current value: {client_id}")
            issues.append("OAUTH_CLIENT_ID needs actual value from Google Cloud Console")
        else:
            print(f"✅ OAUTH_CLIENT_ID: {client_id[:20]}...{client_id[-20:]}")
    else:
        print("❌ OAUTH_CLIENT_ID: NOT SET")
        issues.append("OAUTH_CLIENT_ID is missing")
    
    # Check OAUTH_CLIENT_SECRET
    client_secret = os.getenv('OAUTH_CLIENT_SECRET')
    if client_secret:
        if client_secret.startswith('your_') or len(client_secret) < 10:
            print("⚠️  OAUTH_CLIENT_SECRET: Set but looks like placeholder")
            print(f"   Current value: {client_secret}")
            issues.append("OAUTH_CLIENT_SECRET needs actual value from Google Cloud Console")
        else:
            masked = client_secret[:4] + "*"*(len(client_secret)-8) + client_secret[-4:]
            print(f"✅ OAUTH_CLIENT_SECRET: {masked}")
    else:
        print("❌ OAUTH_CLIENT_SECRET: NOT SET")
        issues.append("OAUTH_CLIENT_SECRET is missing")
    
    # Check OAUTH_REDIRECT_URI
    redirect_uri = os.getenv('OAUTH_REDIRECT_URI')
    expected_uri = "http://localhost:3000/calendar/auth/callback"
    
    if redirect_uri:
        if redirect_uri == expected_uri:
            print(f"✅ OAUTH_REDIRECT_URI: {redirect_uri}")
        else:
            print(f"⚠️  OAUTH_REDIRECT_URI: {redirect_uri}")
            print(f"   Expected: {expected_uri}")
            issues.append(f"OAUTH_REDIRECT_URI should be: {expected_uri}")
    else:
        print(f"ℹ️  OAUTH_REDIRECT_URI: Not set (will use default)")
        print(f"   Default: {expected_uri}")
    
    # Summary
    print("\n" + "="*70)
    if not issues:
        print("✅ CONFIGURATION LOOKS GOOD!")
        print("="*70)
        print("\n📋 Next steps:")
        print("   1. Make sure you added this redirect URI to Google Cloud Console:")
        print(f"      {expected_uri}")
        print("   2. Enable Google Calendar API in Google Cloud Console")
        print("   3. Start your servers:")
        print("      Backend:  uvicorn main:app --reload --port 8000")
        print("      Frontend: npm run dev")
        print("\n✨ Then test the Google Calendar sync feature!")
        return True
    else:
        print("❌ CONFIGURATION ISSUES FOUND")
        print("="*70)
        print("\n🔧 Issues to fix:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n📚 How to fix:")
        print("   1. Go to: https://console.cloud.google.com/apis/credentials")
        print("   2. Find your OAuth 2.0 Client ID")
        print("   3. Copy the Client ID and Client Secret")
        print("   4. Edit backend/.env and paste the values")
        print("   5. Make sure OAUTH_REDIRECT_URI is set to:")
        print(f"      {expected_uri}")
        print("\n📖 See detailed guide: backend/src/OAuth/REDIRECT_URI_FIX.md")
        return False

def check_google_auth_libraries():
    """Check if required libraries are installed"""
    print("\n" + "="*70)
    print("📦 Required Libraries Check:")
    print("="*70 + "\n")
    
    libraries = [
        ('google-auth-oauthlib', 'google_auth_oauthlib'),
        ('google-auth-httplib2', 'google.auth.transport.requests'),
        ('google-api-python-client', 'googleapiclient'),
        ('python-dotenv', 'dotenv'),
    ]
    
    all_installed = True
    
    for package_name, import_name in libraries:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - NOT INSTALLED")
            all_installed = False
    
    if not all_installed:
        print("\n🔧 Install missing libraries:")
        print("   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv")
        return False
    
    return True

def main():
    """Main function"""
    print("\n")
    print("🚀 Lovelace OAuth Configuration Checker")
    print("   This tool helps verify your Google Calendar OAuth setup\n")
    
    # Check libraries first
    libs_ok = check_google_auth_libraries()
    
    # Check configuration
    config_ok = check_oauth_config()
    
    # Final summary
    print("\n" + "="*70)
    if libs_ok and config_ok:
        print("🎉 ALL CHECKS PASSED!")
        print("   Your OAuth configuration is ready to use!")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("   Please fix the issues above and run this script again.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
