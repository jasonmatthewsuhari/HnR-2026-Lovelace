# Lovelace OAuth Module

Comprehensive OAuth2 authentication and Google Calendar integration for the Lovelace Virtual Boyfriend experience.

## Features

### 🔐 OAuth Authentication

- **Google OAuth2 Flow**: Complete authentication flow with access and refresh tokens
- **Token Management**: Automatic token refresh and secure storage
- **User Info Retrieval**: Get user email, name, profile picture
- **Multi-user Support**: Manage multiple user sessions
- **Token Revocation**: Clean logout and credential removal

### 📅 Google Calendar Integration

- **Calendar Listing**: View all user calendars
- **Event Retrieval**: Get upcoming events with customizable timeframes
- **Event Creation**: Create new calendar events programmatically
- **Date-specific Queries**: Get all events for a specific date
- **Occasion Analysis**: AI-powered categorization of events for outfit recommendations

### 💡 Smart Features for Lovelace

- **Outfit Context**: Analyze calendar events to provide outfit recommendations
- **Event Categorization**: Automatically classify events (work, meeting, social, formal, date, casual)
- **Virtual Boyfriend Integration**: Context-aware suggestions based on user's schedule

---

## 📦 Installation

### 1. Install Required Packages

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

Or add to your `requirements.txt`:

```
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
google-api-python-client>=2.0.0
python-dotenv>=1.0.0
```

### 2. Set Up Google Cloud Project

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a New Project** (or select existing)
3. **Enable APIs**:
   - Go to "APIs & Services" > "Library"
   - Search and enable "Google Calendar API"
   - Search and enable "Google+ API" (for user info)
4. **Create OAuth Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Name it (e.g., "Lovelace Desktop Client")
   - Click "Create"
   - **Copy the Client ID and Client Secret** (don't download JSON)

### 3. Configure Environment Variables

1. **Copy the example file**:

   ```bash
   cd backend/src/OAuth
   cp env.example .env
   ```

2. **Edit `.env` file** and add your credentials:

   ```env
   OAUTH_CLIENT_ID=your_actual_client_id.apps.googleusercontent.com
   OAUTH_CLIENT_SECRET=your_actual_client_secret
   OAUTH_REDIRECT_URI=http://localhost:8080/oauth2callback
   ```

3. **IMPORTANT**: The `.env` file is gitignored - never commit it!

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in required fields:
   - App name: "Lovelace"
   - User support email: Your email
   - Developer contact: Your email
4. Add scopes:
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `.../auth/calendar.readonly`
   - `.../auth/calendar.events`
5. Add test users (your Google account)

---

## 🚀 Quick Start

### Run the Interactive Demo

```bash
cd backend/src/OAuth
python demo_oauth.py
```

### Basic Usage Example

```python
from oauth import GoogleOAuthManager, GoogleCalendarManager, authenticate_user

# Initialize OAuth manager (reads from .env automatically)
oauth_manager = GoogleOAuthManager(token_dir='tokens')

# Authenticate user
user_id = "user123"
credentials = authenticate_user(user_id, oauth_manager)

# Get user info
user_info = oauth_manager.get_user_info(credentials)
print(f"Logged in as: {user_info.get('email')}")

# Access calendar
calendar_manager = GoogleCalendarManager(credentials)
events = calendar_manager.get_upcoming_events(days_ahead=7)

for event in events:
    print(f"Event: {event.get('summary')}")
```

### Using Custom Credentials (not from .env)

```python
oauth_manager = GoogleOAuthManager(
    client_id="your_client_id",
    client_secret="your_client_secret",
    token_dir='tokens'
)
```

---

## 📚 API Reference

### GoogleOAuthManager

Main class for handling OAuth authentication.

#### Methods

**`__init__(client_id=None, client_secret=None, token_dir='tokens', redirect_uri='http://localhost:8080/oauth2callback')`**

- Initialize the OAuth manager
- `client_id`: OAuth client ID (reads from OAUTH_CLIENT_ID env var if not provided)
- `client_secret`: OAuth client secret (reads from OAUTH_CLIENT_SECRET env var if not provided)
- `token_dir`: Directory to store user tokens
- `redirect_uri`: OAuth callback URL (reads from OAUTH_REDIRECT_URI env var or uses default)

**`get_authorization_url()`**

- Returns: `(auth_url, flow)` tuple
- Get URL for user to authorize the app

**`exchange_code_for_tokens(flow, authorization_response)`**

- Exchange authorization code for access tokens
- Returns: `Credentials` object

**`save_credentials(user_id, credentials)`**

- Save user credentials to file
- Returns: `True` on success

**`load_credentials(user_id)`**

- Load user credentials from file
- Returns: `Credentials` or `None`

**`get_valid_credentials(user_id)`**

- Get valid credentials, auto-refresh if expired
- Returns: `Credentials` or `None`

**`revoke_credentials(user_id)`**

- Revoke and delete user credentials
- Returns: `True` on success

**`get_user_info(credentials)`**

- Get user profile information
- Returns: Dictionary with user data

### GoogleCalendarManager

Class for interacting with Google Calendar API.

#### Methods

**`__init__(credentials)`**

- Initialize calendar manager with valid credentials

**`list_calendars()`**

- Returns: List of calendar dictionaries

**`get_upcoming_events(calendar_id='primary', max_results=10, days_ahead=7)`**

- Get upcoming events within specified days
- Returns: List of event dictionaries

**`get_events_for_date(date, calendar_id='primary')`**

- Get all events for a specific date
- Returns: List of event dictionaries

**`get_event_details(event_id, calendar_id='primary')`**

- Get detailed information about specific event
- Returns: Event dictionary or `None`

**`create_event(summary, start_time, end_time, description='', location='', calendar_id='primary')`**

- Create a new calendar event
- Returns: Created event dictionary or `None`

**`analyze_occasions(days_ahead=7)`**

- Analyze events and categorize by type
- Returns: Dictionary with occasion analysis

**`get_outfit_recommendations_context()`**

- Get context string for outfit recommendations
- Returns: String describing upcoming occasions

---

## 🎮 Demo Features

The interactive demo (`demo_oauth.py`) includes:

1. **Authenticate New User**: Complete OAuth flow for new user
2. **Test Existing Authentication**: Check if user already authenticated
3. **View Calendar Events**: Display upcoming events
4. **Analyze Occasions**: Get outfit recommendations based on calendar
5. **Create Test Event**: Add a test event to calendar
6. **Revoke Authentication**: Remove user credentials

---

## 🗂️ File Structure

```
backend/src/OAuth/
├── oauth.py              # Main OAuth and Calendar classes
├── demo_oauth.py         # Interactive demo script
├── README.MD             # This file
├── env.example           # Example environment variables file
├── .env                  # Your actual credentials (DO NOT COMMIT)
├── .gitignore           # Git ignore rules
└── tokens/              # Stored user tokens (DO NOT COMMIT)
    └── user_*.pickle    # Individual user token files
```

---

## 🔒 Security Notes

### ⚠️ IMPORTANT: Never commit sensitive files!

Add to `.gitignore`:

```
# OAuth credentials and tokens
.env
tokens/
*.pickle

# Python cache
__pycache__/
*.pyc
```

### Best Practices

1. **Store credentials securely**: Use environment variables in production
2. **Rotate tokens regularly**: Implement token rotation strategy
3. **Use HTTPS**: Always use HTTPS in production redirect URIs
4. **Limit scopes**: Only request necessary OAuth scopes
5. **Validate tokens**: Always check token validity before use

---

## 🐛 Troubleshooting

### Quick Fix: "redirect_uri_mismatch" Error

**See:** `QUICKFIX.md` for a 3-step solution to the most common error!

### Interactive Setup Wizard

Run the setup wizard for guided configuration:

```bash
cd backend/src/OAuth
python setup_oauth_wizard.py
```

This will walk you through the entire setup process step-by-step.

### Configuration Checker

Verify your OAuth configuration:

```bash
cd backend/src/OAuth
python check_oauth_config.py
```

This will check your `.env` file and tell you exactly what's wrong.

### Common Issues

#### "OAuth credentials not found in environment"

- Ensure `.env` file exists in the `backend/` directory (not in OAuth folder)
- Verify OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET are set in `.env`
- Restart your backend server after creating/editing `.env`

#### "Error 400: redirect_uri_mismatch"

**This is the most common error!**

**Quick fix:**

1. Add `http://localhost:3000/calendar/auth/callback` to Google Cloud Console
2. Set `OAUTH_REDIRECT_URI=http://localhost:3000/calendar/auth/callback` in `backend/.env`
3. Restart backend server

**See:** `REDIRECT_URI_FIX.md` for detailed step-by-step guide

#### "Access blocked: This app's request is invalid"

- Check that all required scopes are enabled in OAuth consent screen
- Ensure Calendar API is enabled in Google Cloud Console
- Make sure you added your email as a test user (if app is not published)

#### "Token expired" errors

- The library automatically refreshes tokens
- If refresh fails, user needs to re-authenticate

#### "User not authenticated. Please log in first."

- This means Google OAuth worked, but user isn't logged into Lovelace
- Log into Lovelace app with Firebase first, THEN connect Google Calendar

### Detailed Guides

- **QUICKFIX.md** - 3-step fix for redirect_uri_mismatch
- **REDIRECT_URI_FIX.md** - Complete troubleshooting guide
- **setup_oauth_wizard.py** - Interactive setup wizard
- **check_oauth_config.py** - Configuration verification tool

---

## 🔧 Integration with Lovelace

### Virtual Boyfriend Context

```python
# Get outfit recommendations based on calendar
calendar_manager = GoogleCalendarManager(credentials)
context = calendar_manager.get_outfit_recommendations_context()

# Use context in AI prompt
prompt = f"""
You are the Lovelace Virtual Boyfriend.
{context}
Suggest the perfect outfit for your partner today.
Be caring, attentive, and fashion-forward.
"""
```

### Event-based Notifications

```python
# Check for events today
today_events = calendar_manager.get_events_for_date(datetime.now())

if today_events:
    for event in today_events:
        # Send notification to user
        notify_user(f"Don't forget: {event['summary']} at {event['start']}")
```

---

## 📝 Example Output

```
======================================================================
  LOVELACE OAUTH DEMO
======================================================================

✓ Dependencies installed
✓ Client secrets found: client_secrets.json

----------------------------------------------------------------------
  MAIN MENU
----------------------------------------------------------------------

1. Authenticate new user
2. Test existing user authentication
3. View calendar events
4. Analyze occasions for outfit recommendations
5. Create test calendar event
6. Revoke user authentication
0. Exit

Select an option (0-6): 4

----------------------------------------------------------------------
  OCCASION ANALYSIS FOR OUTFIT RECOMMENDATIONS
----------------------------------------------------------------------

🤖 Virtual Boyfriend is analyzing your calendar...

📊 Analysis Results:
   Total events: 5

📋 Events by Category:

   WORK (2 event(s)):
      • Team Meeting - 2026-01-18T10:00:00Z
      • Project Presentation - 2026-01-20T14:00:00Z

   SOCIAL (1 event(s)):
      • Dinner with Friends - 2026-01-19T19:00:00Z

   DATE (1 event(s)):
      • Movie Night - 2026-01-21T18:30:00Z

💭 Virtual Boyfriend's Outfit Recommendations:

   For your 2 work event(s):
   💼 Professional attire - blazer, dress pants, polished look

   For your 1 social event(s):
   🎉 Fun and stylish - your favorite trendy outfit

   For your 1 date event(s):
   💕 Something special - your most flattering outfit

   'Let me help you pick the perfect outfit!
    I'll make sure you look absolutely stunning! 💖'
```

---

## 🚀 Next Steps

1. **Integrate with main backend**: Connect OAuth to FastAPI endpoints
2. **User profile linking**: Link OAuth user_id with wardrobe database
3. **AI integration**: Use calendar context in outfit recommendation AI
4. **Frontend integration**: Create login button in Next.js frontend
5. **Webhook support**: Set up calendar webhooks for real-time updates

---

## 📄 License

Part of the HnR-2026-Lovelace project.

---

## 🆘 Support

For issues or questions, please check:

- [Google Calendar API Documentation](https://developers.google.com/calendar)
- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
