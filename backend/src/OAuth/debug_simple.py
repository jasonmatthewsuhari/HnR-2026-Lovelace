"""
Debug OAuth Redirect URI - Simple Version
Shows exactly what redirect URI your app is using vs what Google expects
"""

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Load from project root
    project_root = Path(__file__).parent.parent.parent.parent
    env_path = project_root / ".env"
    load_dotenv(env_path)
    print("✓ Environment loaded")
except ImportError:
    print("WARNING: dotenv not installed")
except Exception as e:
    print(f"WARNING: Could not load .env: {e}")

print("\n" + "="*70)
print("OAUTH REDIRECT URI DEBUGGER")
print("="*70 + "\n")

# What your app is configured to use
configured_uri = os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:3000/calendar/auth/callback')
client_id = os.getenv('OAUTH_CLIENT_ID', 'NOT SET')
client_secret = os.getenv('OAUTH_CLIENT_SECRET', 'NOT SET')

print("YOUR CURRENT CONFIGURATION:")
print("-"*70)
if len(client_id) > 50:
    print(f"Client ID: {client_id[:50]}...")
else:
    print(f"Client ID: {client_id}")
print(f"Redirect URI: {configured_uri}")
print()

if client_id == 'NOT SET':
    print("ERROR: OAUTH_CLIENT_ID not set in .env!")
    print("Fix this first before continuing.")
    sys.exit(1)

if client_secret == 'NOT SET':
    print("ERROR: OAUTH_CLIENT_SECRET not set in .env!")
    print("Fix this first before continuing.")
    sys.exit(1)

print("OK: This is what your app will send to Google.")
print("IMPORTANT: Google Cloud Console MUST have the EXACT same URI.\n")

print("="*70)
print("STEP-BY-STEP FIX")
print("="*70 + "\n")

print("STEP 1: COPY this redirect URI (must be EXACT):")
print("-"*70)
print(f">>> {configured_uri} <<<")
print("-"*70)
print()

print("STEP 2: Open Google Cloud Console:")
print("   https://console.cloud.google.com/apis/credentials")
print()

print("STEP 3: Find your OAuth 2.0 Client ID:")
if len(client_id) > 30:
    print(f"   Look for: {client_id[:30]}...")
else:
    print(f"   Look for: {client_id}")
print("   Click on it to edit")
print()

print("STEP 4: Check 'Authorized redirect URIs' section:")
print("   Does it contain EXACTLY:")
print(f"   >>> {configured_uri} <<<")
print()
print("   Check for these problems:")
print("     [X] Extra spaces")
print("     [X] Trailing slash (http://localhost:3000/callback/)")
print("     [X] Wrong port (8000 instead of 3000)")
print("     [X] Typos in path")
print("     [X] http vs https")
print()

print("STEP 5: If NOT found or doesn't match EXACTLY:")
print("   A. Click '+ ADD URI' button")
print(f"   B. Paste: {configured_uri}")
print("   C. Click 'SAVE' button at bottom of page")
print("   D. WAIT 2-3 MINUTES for changes to propagate")
print()

print("STEP 6: These URIs should ALL be in Google Cloud Console:")
print("-"*70)
uris_to_add = [
    "http://localhost:3000/calendar/auth/callback",
    "http://localhost:8000/api/calendar/auth/callback",
]
for i, uri in enumerate(uris_to_add, 1):
    status = "[CURRENT]" if uri == configured_uri else "[ADD THIS]"
    print(f"   {i}. {status} {uri}")
print("-"*70)
print()

print("="*70)
print("TESTING CHECKLIST")
print("="*70 + "\n")

print("After updating Google Cloud Console:")
print()
print("  [ ] Waited 2-3 minutes for Google to propagate changes")
print("  [ ] Cleared browser cache OR using incognito/private window")
print("  [ ] Closed all browser tabs with Google OAuth")
print("  [ ] Opened fresh browser window")
print("  [ ] Backend server is running (uvicorn main:app --reload --port 8000)")
print("  [ ] Frontend server is running (npm run dev)")
print("  [ ] Testing in browser")
print()

print("="*70)
print("HOW TO SEE DETAILED ERROR FROM GOOGLE")
print("="*70 + "\n")

print("When you see 'Error 400: redirect_uri_mismatch':")
print()
print("1. On the error page, look for:")
print("   'If you are a developer of this app, see error details'")
print()
print("2. Click that link - Google will show:")
print("   - What redirect_uri your app sent")
print("   - What redirect_uris are registered in Cloud Console")
print()
print("3. Compare them EXACTLY - even one character difference causes error")
print()

print("="*70)
print("COMMON MISMATCH EXAMPLES")
print("="*70 + "\n")

issues = [
    ("Trailing slash", 
     "WRONG: http://localhost:3000/calendar/auth/callback/",
     "RIGHT: http://localhost:3000/calendar/auth/callback"),
    
    ("Extra spaces",
     "WRONG:  http://localhost:3000/calendar/auth/callback",
     "RIGHT: http://localhost:3000/calendar/auth/callback"),
    
    ("Wrong port",
     "WRONG: http://localhost:8000/calendar/auth/callback",
     "RIGHT: http://localhost:3000/calendar/auth/callback"),
    
    ("HTTP vs HTTPS",
     "WRONG: https://localhost:3000/calendar/auth/callback",
     "RIGHT: http://localhost:3000/calendar/auth/callback"),
    
    ("Missing path",
     "WRONG: http://localhost:3000",
     "RIGHT: http://localhost:3000/calendar/auth/callback"),
]

for i, (issue, wrong, right) in enumerate(issues, 1):
    print(f"{i}. {issue}:")
    print(f"   {wrong}")
    print(f"   {right}")
    print()

print("="*70)
print("VERIFICATION CHECKLIST FOR GOOGLE CLOUD CONSOLE")
print("="*70 + "\n")

print("Go through this checklist:")
print()
print("  [ ] Opened: https://console.cloud.google.com/apis/credentials")
print("  [ ] Selected correct project in top dropdown")
print("  [ ] Found the OAuth 2.0 Client ID section")
print(f"  [ ] Clicked on Client ID: {client_id[:40]}...")
print("  [ ] Scrolled to 'Authorized redirect URIs'")
print(f"  [ ] Verified EXACT match: {configured_uri}")
print("  [ ] No typos, no extra spaces, no trailing slash")
print("  [ ] Clicked 'SAVE' button after adding URI")
print("  [ ] Waited 2-3 minutes after saving")
print("  [ ] Tested in incognito/private browser window")
print()

print("="*70)
print("NUCLEAR OPTION - IF STILL NOT WORKING")
print("="*70 + "\n")

print("Try this drastic approach:")
print()
print("1. In Google Cloud Console, DELETE all existing redirect URIs")
print("2. Add ONLY this one URI:")
print(f"   {configured_uri}")
print("3. Click SAVE")
print("4. Wait 5 FULL minutes (yes, really)")
print("5. Close ALL browser windows")
print("6. Open NEW incognito window")
print("7. Test again")
print()

print("If it STILL doesn't work after this:")
print()
print("1. You might have multiple OAuth Client IDs in Google Cloud")
print("   - Check if you're editing the correct one")
print(f"   - Your .env has: {client_id[:40]}...")
print("   - Make sure this matches what you're editing")
print()
print("2. Create a BRAND NEW OAuth Client ID:")
print("   - In Google Cloud Console, click 'CREATE CREDENTIALS'")
print("   - Choose 'OAuth client ID'")
print("   - Application type: 'Web application'")
print("   - Name: 'Lovelace-Fresh'")
print(f"   - Authorized redirect URIs: {configured_uri}")
print("   - Click 'CREATE'")
print("   - Copy the NEW Client ID and Client Secret")
print("   - Update your .env file with new credentials")
print("   - Restart backend server")
print("   - Test again")
print()

print("="*70)
print("NEXT STEPS")
print("="*70 + "\n")

print("1. Follow the steps above to fix Google Cloud Console")
print("2. Run check_oauth_config.py to verify your .env")
print("3. Restart your backend server")
print("4. Test in incognito window")
print()
print("If you need more help, share the EXACT error message from Google")
print("(including what they say the redirect_uri mismatch is)")
print()
print("="*70 + "\n")
