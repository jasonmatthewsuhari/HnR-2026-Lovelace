"""
Debug OAuth Redirect URI
Shows exactly what redirect URI your app is using vs what Google expects
"""

import os
import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

try:
    from dotenv import load_dotenv
    # Load from project root
    project_root = Path(__file__).parent.parent.parent.parent
    env_path = project_root / ".env"
    load_dotenv(env_path)
except ImportError:
    print("Warning: dotenv not installed")

print("\n" + "="*70)
print("OAUTH REDIRECT URI DEBUGGER")
print("="*70 + "\n")

# What your app is configured to use
configured_uri = os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:3000/calendar/auth/callback')
client_id = os.getenv('OAUTH_CLIENT_ID', 'NOT SET')

print("📋 Your Current Configuration:")
print("-"*70)
print(f"Client ID: {client_id[:50]}...")
print(f"Redirect URI: {configured_uri}")
print()

print("✅ This is what your app will send to Google.")
print("⚠️  Google Cloud Console MUST have the EXACT same URI.\n")

print("="*70)
print("🔧 STEP-BY-STEP FIX")
print("="*70 + "\n")

print("1️⃣  COPY this redirect URI (it MUST be EXACT):")
print("-"*70)
print(f"   {configured_uri}")
print("-"*70)
print()

print("2️⃣  Open Google Cloud Console:")
print(f"   https://console.cloud.google.com/apis/credentials")
print()

print("3️⃣  Find your OAuth 2.0 Client ID:")
print(f"   Look for: {client_id[:30]}...")
print("   Click on it to edit")
print()

print("4️⃣  Check 'Authorized redirect URIs' section:")
print("   • Look for EXACT match of your redirect URI")
print("   • Check for:")
print("     ❌ Extra spaces")
print("     ❌ Trailing slash (http://localhost:3000/callback/)")
print("     ❌ Wrong port")
print("     ❌ Typos")
print()

print("5️⃣  If NOT found or doesn't match EXACTLY:")
print("   • Click '+ ADD URI'")
print(f"   • Paste: {configured_uri}")
print("   • Click 'SAVE' at bottom")
print("   • WAIT 2-3 MINUTES for changes to propagate")
print()

print("6️⃣  Additional URIs to add (for different scenarios):")
print("-"*70)
uris_to_add = [
    "http://localhost:3000/calendar/auth/callback",
    "http://localhost:8000/api/calendar/auth/callback",
    "http://localhost:8080"
]
for uri in uris_to_add:
    status = "✅ Current" if uri == configured_uri else "➕ Add this too"
    print(f"   {status}: {uri}")
print("-"*70)
print()

print("="*70)
print("🧪 TESTING TIPS")
print("="*70 + "\n")

print("After updating Google Cloud Console:")
print()
print("1. ⏱️  WAIT 2-3 minutes for Google to propagate changes")
print("2. 🔄 Clear browser cache OR use incognito/private window")
print("3. 🚫 Close all browser tabs with Google OAuth")
print("4. 🆕 Open fresh browser window")
print("5. 🧪 Test again")
print()

print("="*70)
print("🔎 HOW TO SEE DETAILED ERROR FROM GOOGLE")
print("="*70 + "\n")

print("If you see 'Error 400: redirect_uri_mismatch':")
print()
print("1. On the error page, click 'Learn more about this error'")
print("   OR click 'error details' (if you're a developer)")
print()
print("2. Google will show:")
print("   • What redirect_uri your app sent")
print("   • What redirect_uris are registered")
print()
print("3. Copy what Google shows and compare EXACTLY")
print()

print("="*70)
print("🐛 COMMON ISSUES")
print("="*70 + "\n")

issues = [
    ("Trailing slash", 
     "http://localhost:3000/calendar/auth/callback/ ❌",
     "http://localhost:3000/calendar/auth/callback ✅"),
    
    ("Extra spaces",
     " http://localhost:3000/calendar/auth/callback ❌",
     "http://localhost:3000/calendar/auth/callback ✅"),
    
    ("Wrong port",
     "http://localhost:8000/calendar/auth/callback ❌",
     "http://localhost:3000/calendar/auth/callback ✅"),
    
    ("HTTP vs HTTPS",
     "https://localhost:3000/calendar/auth/callback ❌",
     "http://localhost:3000/calendar/auth/callback ✅"),
]

for i, (issue, wrong, right) in enumerate(issues, 1):
    print(f"{i}. {issue}:")
    print(f"   Wrong: {wrong}")
    print(f"   Right: {right}")
    print()

print("="*70)
print("🔑 VERIFY YOUR GOOGLE CLOUD CONSOLE")
print("="*70 + "\n")

print("Quick checklist:")
print()
print("□ Opened: https://console.cloud.google.com/apis/credentials")
print("□ Selected correct project")
print("□ Clicked on OAuth 2.0 Client ID")
print("□ Found 'Authorized redirect URIs' section")
print("□ Verified EXACT match (no typos, no extra spaces, no trailing slash)")
print("□ If added new URI, clicked 'SAVE' button")
print("□ Waited 2-3 minutes after saving")
print("□ Tested in incognito/private browser window")
print()

print("="*70)
print("🆘 STILL NOT WORKING?")
print("="*70 + "\n")

print("Try this:")
print()
print("1. In Google Cloud Console, REMOVE all redirect URIs")
print("2. Add ONLY this one:")
print(f"   {configured_uri}")
print("3. Save and wait 5 minutes")
print("4. Test in incognito window")
print()

print("If it STILL doesn't work:")
print()
print("1. Check if you have multiple OAuth Client IDs")
print("   • You might be editing the wrong one")
print("   • Make sure the Client ID matches your .env file")
print()
print("2. Create a NEW OAuth Client ID:")
print("   • Type: Web application")
print("   • Name: Lovelace-New")
print(f"   • Redirect URI: {configured_uri}")
print("   • Copy the NEW Client ID and Secret to your .env")
print("   • Restart backend server")
print()

print("="*70)
print("📧 SHOW ERROR DETAILS")
print("="*70 + "\n")

print("When you see the error page, look for:")
print()
print("• 'If you are a developer of this app, see error details'")
print("• Click that link")
print("• It will show the EXACT mismatch")
print("• Share that info if you need more help")
print()

print("="*70 + "\n")
