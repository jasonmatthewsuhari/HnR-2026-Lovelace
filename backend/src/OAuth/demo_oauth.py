"""
Lovelace OAuth Demo - Interactive Testing Script

This script provides an interactive demo for testing:
1. Google OAuth2 authentication
2. Google Calendar integration
3. Occasion analysis for outfit recommendations

Usage:
    python demo_oauth.py
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from oauth import (
        GoogleOAuthManager,
        GoogleCalendarManager,
        authenticate_user,
        GOOGLE_AUTH_AVAILABLE
    )
except ImportError as e:
    print(f"Error importing oauth module: {e}")
    sys.exit(1)


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(text: str):
    """Print a formatted section"""
    print("\n" + "-"*70)
    print(f"  {text}")
    print("-"*70)


def demo_oauth_flow():
    """Demo the OAuth authentication flow"""
    print_header("LOVELACE OAUTH DEMO")
    
    if not GOOGLE_AUTH_AVAILABLE:
        print("\n❌ ERROR: Google Auth libraries not installed!")
        print("\nPlease install required packages:")
        print("  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv")
        return False
    
    # Check for environment variables
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv('OAUTH_CLIENT_ID')
    client_secret = os.getenv('OAUTH_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print(f"\n❌ ERROR: OAuth credentials not found in .env file!")
        print("\n📋 To set up your credentials:")
        print("   1. Create a .env file in the OAuth directory")
        print("   2. Add these lines:")
        print("      OAUTH_CLIENT_ID=your_client_id_here")
        print("      OAUTH_CLIENT_SECRET=your_client_secret_here")
        print("\n   Get credentials from: https://console.cloud.google.com/")
        print("   Go to: APIs & Services > Credentials > Create OAuth Client ID")
        print(f"\n   .env file location: {os.path.abspath('.env')}")
        return False
    
    print("\n✓ Dependencies installed")
    print(f"✓ OAuth credentials loaded from .env")
    
    return True


def interactive_menu():
    """Display interactive menu"""
    print_section("MAIN MENU")
    print("\n1. Authenticate new user")
    print("2. Test existing user authentication")
    print("3. View calendar events")
    print("4. Analyze occasions for outfit recommendations")
    print("5. Create test calendar event")
    print("6. Revoke user authentication")
    print("0. Exit")
    
    choice = input("\nSelect an option (0-6): ").strip()
    return choice


def test_authentication():
    """Test user authentication"""
    print_section("USER AUTHENTICATION")
    
    user_id = input("\nEnter user ID (or press Enter for 'lovelace_test_user'): ").strip()
    if not user_id:
        user_id = "lovelace_test_user"
    
    print(f"\n🔐 Authenticating user: {user_id}")
    
    oauth_manager = GoogleOAuthManager(token_dir='tokens')
    
    credentials = authenticate_user(user_id, oauth_manager)
    
    if credentials:
        print("\n✅ Authentication successful!")
        
        # Get user info
        user_info = oauth_manager.get_user_info(credentials)
        if user_info:
            print(f"\n👤 User Information:")
            print(f"   Email: {user_info.get('email')}")
            print(f"   Name: {user_info.get('name')}")
            print(f"   ID: {user_info.get('id')}")
            if user_info.get('picture'):
                print(f"   Picture: {user_info.get('picture')}")
        
        return user_id, credentials
    else:
        print("\n❌ Authentication failed!")
        return None, None


def view_calendar_events(credentials):
    """View calendar events"""
    print_section("CALENDAR EVENTS")
    
    calendar_manager = GoogleCalendarManager(credentials)
    
    # List calendars
    print("\n📅 Your Calendars:")
    calendars = calendar_manager.list_calendars()
    if not calendars:
        print("   No calendars found.")
        return
    
    for i, cal in enumerate(calendars, 1):
        primary = " (Primary)" if cal.get('primary') else ""
        print(f"   {i}. {cal.get('summary')}{primary}")
    
    # Get upcoming events
    print("\n📆 Upcoming Events (Next 7 Days):")
    events = calendar_manager.get_upcoming_events(days_ahead=7, max_results=10)
    
    if not events:
        print("   No upcoming events found.")
        print("   Perfect time for casual, comfortable outfits! 👕")
    else:
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            location = event.get('location', '')
            
            print(f"\n   {i}. {summary}")
            print(f"      📍 Time: {start}")
            if location:
                print(f"      📍 Location: {location}")
            if event.get('description'):
                desc = event['description'][:100]
                print(f"      📝 {desc}{'...' if len(event['description']) > 100 else ''}")


def analyze_occasions(credentials):
    """Analyze occasions for outfit recommendations"""
    print_section("OCCASION ANALYSIS FOR OUTFIT RECOMMENDATIONS")
    
    calendar_manager = GoogleCalendarManager(credentials)
    
    print("\n🤖 Virtual Boyfriend is analyzing your calendar...")
    occasions = calendar_manager.analyze_occasions(days_ahead=7)
    
    print(f"\n📊 Analysis Results:")
    print(f"   Total events: {occasions['total_events']}")
    
    if occasions['total_events'] == 0:
        print("\n💭 Virtual Boyfriend says:")
        print('   "You have no upcoming events! How about we go shopping together?')
        print('    I\'d love to see you in something casual and comfortable. 😊"')
        return
    
    print("\n📋 Events by Category:")
    outfit_suggestions = {
        'work': '💼 Professional attire - blazer, dress pants, polished look',
        'meeting': '👔 Smart casual - button-up shirt, neat presentation',
        'social': '🎉 Fun and stylish - your favorite trendy outfit',
        'formal': '✨ Formal wear - elegant dress or suit',
        'date': '💕 Something special - your most flattering outfit',
        'casual': '👕 Relaxed and comfortable - jeans and nice top'
    }
    
    recommendations = []
    
    for event_type, events in occasions['by_type'].items():
        if events:
            print(f"\n   {event_type.upper()} ({len(events)} event(s)):")
            for event in events:
                print(f"      • {event['summary']} - {event['start']}")
            
            if event_type in outfit_suggestions:
                recommendations.append({
                    'type': event_type,
                    'count': len(events),
                    'suggestion': outfit_suggestions[event_type]
                })
    
    if recommendations:
        print("\n💭 Virtual Boyfriend's Outfit Recommendations:")
        for rec in recommendations:
            print(f"\n   For your {rec['count']} {rec['type']} event(s):")
            print(f"   {rec['suggestion']}")
        
        print("\n   'Let me help you pick the perfect outfit! ")
        print("    I'll make sure you look absolutely stunning! 💖'")


def create_test_event(credentials):
    """Create a test calendar event"""
    print_section("CREATE TEST EVENT")
    
    calendar_manager = GoogleCalendarManager(credentials)
    
    print("\n📝 Creating a test event...")
    
    summary = input("Event title (or press Enter for 'Shopping with Lovelace'): ").strip()
    if not summary:
        summary = "Shopping with Lovelace 💕"
    
    # Default to tomorrow at 2pm for 1 hour
    start_time = datetime.now() + timedelta(days=1)
    start_time = start_time.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    
    description = "Virtual shopping date with my Lovelace boyfriend! 🛍️💖"
    location = "Virtual Mall"
    
    print(f"\n   Title: {summary}")
    print(f"   Start: {start_time}")
    print(f"   End: {end_time}")
    print(f"   Description: {description}")
    print(f"   Location: {location}")
    
    confirm = input("\nCreate this event? (y/n): ").strip().lower()
    
    if confirm == 'y':
        event = calendar_manager.create_event(
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location
        )
        
        if event:
            print("\n✅ Event created successfully!")
            print(f"   Event ID: {event.get('id')}")
            if event.get('htmlLink'):
                print(f"   View: {event.get('htmlLink')}")
        else:
            print("\n❌ Failed to create event")
    else:
        print("\n❌ Event creation cancelled")


def revoke_authentication():
    """Revoke user authentication"""
    print_section("REVOKE AUTHENTICATION")
    
    oauth_manager = GoogleOAuthManager(token_dir='tokens')
    
    user_id = input("\nEnter user ID to revoke: ").strip()
    if not user_id:
        print("❌ User ID required")
        return
    
    confirm = input(f"\n⚠️  Revoke authentication for '{user_id}'? (y/n): ").strip().lower()
    
    if confirm == 'y':
        oauth_manager.revoke_credentials(user_id)
        print(f"\n✅ Authentication revoked for user: {user_id}")
    else:
        print("\n❌ Revocation cancelled")


def main():
    """Main interactive demo"""
    # Initial setup check
    if not demo_oauth_flow():
        return
    
    current_user = None
    current_credentials = None
    
    print("\n✨ Welcome to Lovelace OAuth Demo!")
    print("   Let's test Google authentication and calendar integration")
    
    while True:
        try:
            if current_user:
                print(f"\n👤 Current user: {current_user}")
            
            choice = interactive_menu()
            
            if choice == '0':
                print("\n👋 Goodbye! Thanks for testing Lovelace!")
                break
            
            elif choice == '1':
                current_user, current_credentials = test_authentication()
            
            elif choice == '2':
                user_id = input("\nEnter user ID: ").strip()
                if user_id:
                    oauth_manager = GoogleOAuthManager(token_dir='tokens')
                    creds = oauth_manager.get_valid_credentials(user_id)
                    if creds:
                        current_user = user_id
                        current_credentials = creds
                        print(f"\n✅ User {user_id} already authenticated!")
                        user_info = oauth_manager.get_user_info(creds)
                        if user_info:
                            print(f"   Email: {user_info.get('email')}")
                    else:
                        print(f"\n❌ User {user_id} not authenticated. Please authenticate first.")
            
            elif choice == '3':
                if current_credentials:
                    view_calendar_events(current_credentials)
                else:
                    print("\n❌ Please authenticate first (option 1 or 2)")
            
            elif choice == '4':
                if current_credentials:
                    analyze_occasions(current_credentials)
                else:
                    print("\n❌ Please authenticate first (option 1 or 2)")
            
            elif choice == '5':
                if current_credentials:
                    create_test_event(current_credentials)
                else:
                    print("\n❌ Please authenticate first (option 1 or 2)")
            
            elif choice == '6':
                revoke_authentication()
                if current_user:
                    current_user = None
                    current_credentials = None
            
            else:
                print("\n❌ Invalid option. Please select 0-6.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
