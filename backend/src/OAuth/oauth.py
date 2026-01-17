"""
Lovelace OAuth Module - Google Authentication & Calendar Integration

This module provides comprehensive OAuth2 authentication for Google services,
including Google Calendar integration for the Lovelace Virtual Boyfriend experience.

Main features:
- Google OAuth2 authentication flow
- Token management (access & refresh tokens)
- Google Calendar API integration
- Session management
- Token storage and retrieval
"""

import os

# CRITICAL: Set this BEFORE importing Google OAuth libraries
# This allows OAuth to work with HTTP on localhost for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
print("✓ Enabled HTTP for OAuth development (localhost)")

import json
import pickle
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("Warning: python-dotenv not installed. Run: pip install python-dotenv")

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow, InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    print("Warning: Google Auth libraries not installed.")
    print("Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")


# OAuth scopes for Google services
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events',
]


class GoogleOAuthManager:
    """
    Manages Google OAuth2 authentication and token lifecycle
    """
    
    def __init__(self, 
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 token_dir: str = 'tokens',
                 redirect_uri: str = 'http://localhost:8080/oauth2callback'):
        """
        Initialize Google OAuth Manager
        
        Args:
            client_id: OAuth client ID (from .env or parameter)
            client_secret: OAuth client secret (from .env or parameter)
            token_dir: Directory to store user tokens
            redirect_uri: OAuth redirect URI (from .env or parameter)
        """
        if not GOOGLE_AUTH_AVAILABLE:
            raise ImportError("Google Auth libraries not installed")
        
        # Load from environment variables if not provided
        self.client_id = client_id or os.getenv('OAUTH_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('OAUTH_CLIENT_SECRET')
        self.redirect_uri = os.getenv('OAUTH_REDIRECT_URI', redirect_uri)
        
        self.token_dir = Path(token_dir)
        self.token_dir.mkdir(exist_ok=True)
        
        # Verify credentials are available
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "OAuth credentials not found. Please set OAUTH_CLIENT_ID and "
                "OAUTH_CLIENT_SECRET in your .env file or pass them as parameters."
            )
    
    def get_token_path(self, user_id: str) -> Path:
        """Get the path to a user's token file"""
        return self.token_dir / f"{user_id}_token.pickle"
    
    def initiate_oauth_flow(self) -> Flow:
        """
        Initiate OAuth2 flow for user authentication
        
        Returns:
            Flow object for OAuth2 authentication
        """
        # Use web application configuration for better localhost support
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [self.redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=self.redirect_uri
        )

        # For localhost development, allow HTTP
        if self.redirect_uri.startswith('http://localhost'):
            import os
            # Disable HTTPS requirement for localhost development
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        return flow
    
    def get_authorization_url(self) -> tuple[str, Flow]:
        """
        Get the authorization URL for user to grant permissions
        
        Returns:
            Tuple of (authorization_url, flow_object)
        """
        flow = self.initiate_oauth_flow()
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        return auth_url, flow
    
    def exchange_code_for_tokens(self, flow: Flow, authorization_response: str) -> Credentials:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            flow: The Flow object from get_authorization_url
            authorization_response: The full callback URL with code
            
        Returns:
            Credentials object with tokens
        """
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        return credentials
    
    def save_credentials(self, user_id: str, credentials: Credentials) -> bool:
        """
        Save user credentials to file
        
        Args:
            user_id: Unique user identifier
            credentials: Google OAuth credentials
            
        Returns:
            True if successful
        """
        token_path = self.get_token_path(user_id)
        with open(token_path, 'wb') as token_file:
            pickle.dump(credentials, token_file)
        print(f"✓ Credentials saved for user: {user_id}")
        return True
    
    def load_credentials(self, user_id: str) -> Optional[Credentials]:
        """
        Load user credentials from file
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Credentials object or None if not found
        """
        token_path = self.get_token_path(user_id)
        if not token_path.exists():
            return None
        
        with open(token_path, 'rb') as token_file:
            credentials = pickle.load(token_file)
        return credentials
    
    def refresh_credentials(self, credentials: Credentials) -> Credentials:
        """
        Refresh expired credentials using refresh token
        
        Args:
            credentials: Expired credentials with refresh token
            
        Returns:
            Refreshed credentials
        """
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            print("✓ Credentials refreshed")
        return credentials
    
    def get_valid_credentials(self, user_id: str) -> Optional[Credentials]:
        """
        Get valid credentials for a user, refreshing if necessary
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Valid credentials or None if authentication needed
        """
        credentials = self.load_credentials(user_id)
        if not credentials:
            return None
        
        if credentials.expired and credentials.refresh_token:
            credentials = self.refresh_credentials(credentials)
            self.save_credentials(user_id, credentials)
        
        return credentials
    
    def revoke_credentials(self, user_id: str) -> bool:
        """
        Revoke and delete user credentials
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            True if successful
        """
        token_path = self.get_token_path(user_id)
        if token_path.exists():
            token_path.unlink()
            print(f"✓ Credentials revoked for user: {user_id}")
        return True
    
    def get_user_info(self, credentials: Credentials) -> Dict[str, Any]:
        """
        Get user information from Google
        
        Args:
            credentials: Valid Google OAuth credentials
            
        Returns:
            Dictionary with user info (email, name, picture, etc.)
        """
        try:
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            return user_info
        except HttpError as error:
            print(f"Error getting user info: {error}")
            return {}


class GoogleCalendarManager:
    """
    Manages Google Calendar API interactions for the Lovelace Virtual Boyfriend
    """
    
    def __init__(self, credentials: Credentials):
        """
        Initialize Google Calendar Manager
        
        Args:
            credentials: Valid Google OAuth credentials
        """
        if not GOOGLE_AUTH_AVAILABLE:
            raise ImportError("Google Auth libraries not installed")
        
        self.credentials = credentials
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        List all calendars accessible to the user
        
        Returns:
            List of calendar dictionaries
        """
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            return calendars
        except HttpError as error:
            print(f"Error listing calendars: {error}")
            return []
    
    def get_upcoming_events(self, 
                           calendar_id: str = 'primary',
                           max_results: int = 10,
                           days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Get upcoming events from a calendar
        
        Args:
            calendar_id: Calendar ID (default: 'primary')
            max_results: Maximum number of events to return
            days_ahead: Number of days to look ahead
            
        Returns:
            List of event dictionaries
        """
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
        except HttpError as error:
            print(f"Error getting events: {error}")
            return []
    
    def get_events_for_date(self, 
                           date: datetime,
                           calendar_id: str = 'primary') -> List[Dict[str, Any]]:
        """
        Get all events for a specific date
        
        Args:
            date: Date to get events for
            calendar_id: Calendar ID (default: 'primary')
            
        Returns:
            List of event dictionaries
        """
        try:
            # Set time range for the entire day
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            time_min = start_of_day.isoformat() + 'Z'
            time_max = end_of_day.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
        except HttpError as error:
            print(f"Error getting events for date: {error}")
            return []
    
    def get_event_details(self, event_id: str, calendar_id: str = 'primary') -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific event
        
        Args:
            event_id: Event ID
            calendar_id: Calendar ID (default: 'primary')
            
        Returns:
            Event dictionary or None
        """
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return event
        except HttpError as error:
            print(f"Error getting event details: {error}")
            return None
    
    def create_event(self,
                    summary: str,
                    start_time: datetime,
                    end_time: datetime,
                    description: str = '',
                    location: str = '',
                    calendar_id: str = 'primary') -> Optional[Dict[str, Any]]:
        """
        Create a new calendar event
        
        Args:
            summary: Event title
            start_time: Start datetime
            end_time: End datetime
            description: Event description
            location: Event location
            calendar_id: Calendar ID (default: 'primary')
            
        Returns:
            Created event dictionary or None
        """
        try:
            event = {
                'summary': summary,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            print(f"✓ Event created: {created_event.get('htmlLink')}")
            return created_event
        except HttpError as error:
            print(f"Error creating event: {error}")
            return None
    
    def analyze_occasions(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Analyze upcoming events to identify special occasions for outfit recommendations
        
        Args:
            days_ahead: Number of days to analyze
            
        Returns:
            Dictionary with occasion analysis
        """
        events = self.get_upcoming_events(days_ahead=days_ahead)
        
        occasions = {
            'total_events': len(events),
            'by_type': {
                'work': [],
                'meeting': [],
                'social': [],
                'formal': [],
                'casual': [],
                'date': [],
                'other': []
            },
            'special_occasions': []
        }
        
        # Keywords for categorizing events
        keywords = {
            'work': ['meeting', 'work', 'office', 'presentation', 'conference'],
            'meeting': ['meeting', 'call', 'zoom', 'teams'],
            'social': ['party', 'dinner', 'lunch', 'gathering', 'hangout'],
            'formal': ['formal', 'gala', 'wedding', 'ceremony', 'interview'],
            'date': ['date', 'romantic', 'anniversary'],
            'casual': ['casual', 'coffee', 'walk', 'brunch']
        }
        
        for event in events:
            summary = event.get('summary', '').lower()
            description = event.get('description', '').lower()
            combined_text = f"{summary} {description}"
            
            event_info = {
                'summary': event.get('summary'),
                'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date')),
                'location': event.get('location', '')
            }
            
            # Categorize event
            categorized = False
            for category, category_keywords in keywords.items():
                if any(keyword in combined_text for keyword in category_keywords):
                    occasions['by_type'][category].append(event_info)
                    categorized = True
                    break
            
            if not categorized:
                occasions['by_type']['other'].append(event_info)
        
        return occasions
    
    def get_outfit_recommendations_context(self) -> str:
        """
        Get context string for outfit recommendations based on upcoming calendar events
        
        Returns:
            String describing upcoming occasions
        """
        occasions = self.analyze_occasions()
        
        if occasions['total_events'] == 0:
            return "No upcoming events in your calendar. Perfect time for casual, comfortable outfits!"
        
        context_parts = [f"You have {occasions['total_events']} upcoming event(s):"]
        
        for event_type, events in occasions['by_type'].items():
            if events:
                context_parts.append(f"- {len(events)} {event_type} event(s)")
        
        return " ".join(context_parts)


def authenticate_user(user_id: str, 
                     oauth_manager: GoogleOAuthManager,
                     use_local_server: bool = True) -> Optional[Credentials]:
    """
    Complete authentication flow for a user with automatic browser popup
    
    Args:
        user_id: Unique user identifier
        oauth_manager: GoogleOAuthManager instance
        use_local_server: If True, opens browser and handles callback automatically (default: True)
        
    Returns:
        Valid credentials or None
    """
    # Check if user already has valid credentials
    credentials = oauth_manager.get_valid_credentials(user_id)
    if credentials:
        print(f"✓ User {user_id} already authenticated")
        return credentials
    
    # Start new OAuth flow
    print(f"\n🔐 Starting authentication for user: {user_id}")
    
    print("\n" + "="*70)
    print("AUTHENTICATION - BROWSER WILL OPEN AUTOMATICALLY")
    print("="*70)
    print("\n1. Your browser will open with Google login")
    print("2. Sign in with your Google account")
    print("3. Grant permissions to Lovelace")
    print("4. Browser will show 'Authentication successful' or close automatically")
    print("5. Return to this terminal")
    print("\n" + "="*70)
    print("\n⏳ Opening browser in 3 seconds...")
    
    import time
    time.sleep(2)
    
    if use_local_server:
        try:
            print("🌐 Starting local authentication server...")
            print("🔓 Opening browser for Google login...\n")
            
            # Create flow for local server
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": oauth_manager.client_id,
                        "client_secret": oauth_manager.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "redirect_uris": ["http://localhost:8080/"]
                    }
                },
                scopes=SCOPES
            )
            
            # This automatically:
            # 1. Starts a local server on port 8080
            # 2. Opens the browser to Google login
            # 3. Handles the callback when user authorizes
            # 4. Returns the credentials
            credentials = flow.run_local_server(
                port=8080,
                open_browser=True,
                authorization_prompt_message='',
                success_message='✅ Authentication successful! You can close this window and return to the terminal.',
                bind_addr='localhost'
            )
            
            print("\n✅ Browser authentication completed!")
            
        except Exception as e:
            print(f"\n⚠️  Error with browser authentication: {e}")
            print("\nFalling back to manual method...")
            use_local_server = False
    
    if not use_local_server:
        # Fallback to manual copy-paste method
        auth_url, flow = oauth_manager.get_authorization_url()
        
        print("\n📋 MANUAL AUTHENTICATION METHOD")
        print("="*70)
        print(f"\nPlease visit this URL in your browser:")
        print(f"\n{auth_url}\n")
        print("After authorization, copy the ENTIRE redirect URL and paste below.")
        print("="*70 + "\n")
        
        authorization_response = input("Paste the full redirect URL here: ").strip()
        credentials = oauth_manager.exchange_code_for_tokens(flow, authorization_response)
    
    # Save credentials
    oauth_manager.save_credentials(user_id, credentials)
    
    print(f"\n✅ Authentication successful for user: {user_id}")
    return credentials


def main():
    """
    Main function demonstrating OAuth and Calendar integration
    """
    print("=" * 60)
    print("Lovelace OAuth & Google Calendar Demo")
    print("=" * 60)
    print()
    
    if not GOOGLE_AUTH_AVAILABLE:
        print("ERROR: Google Auth libraries not installed!")
        print("Please run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return
    
    # Check for environment variables
    if not os.getenv('OAUTH_CLIENT_ID') or not os.getenv('OAUTH_CLIENT_SECRET'):
        print("ERROR: OAuth credentials not found in environment!")
        print("\nPlease create a .env file with:")
        print("  OAUTH_CLIENT_ID=your_client_id")
        print("  OAUTH_CLIENT_SECRET=your_client_secret")
        print("\nTo get your credentials:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Calendar API")
        print("4. Go to: APIs & Services > Credentials")
        print("5. Create OAuth 2.0 Client ID (Desktop app)")
        print("6. Copy Client ID and Client Secret to .env file")
        print()
        return
    
    try:
        # Initialize OAuth manager
        oauth_manager = GoogleOAuthManager(token_dir='tokens')
        
        # Test user ID
        test_user_id = "lovelace_user_001"
        
        # Authenticate user
        print(f"Authenticating user: {test_user_id}\n")
        credentials = authenticate_user(test_user_id, oauth_manager)
        
        if not credentials:
            print("Authentication failed!")
            return
        
        # Get user info
        print("\nFetching user information...")
        user_info = oauth_manager.get_user_info(credentials)
        if user_info:
            print(f"✓ Logged in as: {user_info.get('email')}")
            print(f"  Name: {user_info.get('name')}")
            print(f"  Picture: {user_info.get('picture')}")
        
        # Initialize Calendar manager
        print("\n" + "="*60)
        print("Google Calendar Integration")
        print("="*60 + "\n")
        
        calendar_manager = GoogleCalendarManager(credentials)
        
        # List calendars
        print("Your calendars:")
        calendars = calendar_manager.list_calendars()
        for i, cal in enumerate(calendars, 1):
            print(f"  {i}. {cal.get('summary')} ({cal.get('id')})")
        print()
        
        # Get upcoming events
        print("Upcoming events (next 7 days):")
        events = calendar_manager.get_upcoming_events(days_ahead=7)
        
        if not events:
            print("  No upcoming events found.")
        else:
            for i, event in enumerate(events, 1):
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"  {i}. {event.get('summary', 'No title')} - {start}")
        print()
        
        # Analyze occasions for outfit recommendations
        print("Outfit recommendation context:")
        print("-" * 60)
        occasions = calendar_manager.analyze_occasions(days_ahead=7)
        context = calendar_manager.get_outfit_recommendations_context()
        print(context)
        print()
        
        print("Detailed occasion breakdown:")
        for event_type, events in occasions['by_type'].items():
            if events:
                print(f"\n{event_type.upper()} ({len(events)} event(s)):")
                for event in events:
                    print(f"  • {event['summary']} - {event['start']}")
        
        print("\n" + "="*60)
        print("✓ Demo completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
