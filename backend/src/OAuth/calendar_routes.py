"""
FastAPI routes for Google Calendar integration in Lovelace

Provides endpoints for:
- Google OAuth authentication
- Calendar listing and management
- Event retrieval and creation
- Outfit recommendation context from calendar events
"""

import os

# CRITICAL: Set this BEFORE importing oauth module
# This allows OAuth to work with HTTP on localhost for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .oauth import GoogleOAuthManager, GoogleCalendarManager

# Initialize router
router = APIRouter(prefix="/api/calendar", tags=["Google Calendar"])

# Initialize OAuth manager
try:
    oauth_manager = GoogleOAuthManager(token_dir='tokens')
    OAUTH_AVAILABLE = True
except Exception as e:
    print(f"Warning: OAuth not available: {e}")
    oauth_manager = None
    OAUTH_AVAILABLE = False


def get_oauth_manager():
    """Dependency to get OAuth manager"""
    if not OAUTH_AVAILABLE:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    # Update redirect URI for web app
    oauth_manager.redirect_uri = os.getenv('OAUTH_REDIRECT_URI', 'http://localhost:3000/calendar/auth/callback')
    return oauth_manager


def get_calendar_manager(user_id: str, oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)) -> GoogleCalendarManager:
    """Dependency to get calendar manager for authenticated user"""
    credentials = oauth_manager.get_valid_credentials(user_id)
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated with Google. Please authenticate first."
        )

    try:
        return GoogleCalendarManager(credentials)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize calendar manager: {str(e)}")


@router.get("/auth/{user_id}")
async def initiate_google_auth(user_id: str, oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)):
    """
    Initiate Google OAuth authentication for a user

    Args:
        user_id: Unique user identifier

    Returns:
        Redirect to Google OAuth consent screen
    """
    try:
        auth_url, flow = oauth_manager.get_authorization_url()

        # In a production app, you'd store the flow state securely
        # For now, we'll return the auth URL for the frontend to handle
        return {
            "auth_url": auth_url,
            "message": "Redirect user to this URL to authenticate with Google"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate authentication: {str(e)}")


@router.post("/auth/callback/{user_id}")
async def handle_oauth_callback(
    user_id: str,
    authorization_response: str = Query(..., description="Full authorization response URL"),
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """
    Handle OAuth callback and store credentials

    Args:
        user_id: Unique user identifier
        authorization_response: Full callback URL with authorization code

    Returns:
        Success message
    """
    try:
        # Get the flow (in production, you'd retrieve from secure storage)
        flow = oauth_manager.initiate_oauth_flow()

        # Exchange code for tokens
        credentials = oauth_manager.exchange_code_for_tokens(flow, authorization_response)

        # Save credentials
        oauth_manager.save_credentials(user_id, credentials)

        return {
            "message": "Authentication successful",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/auth/status/{user_id}")
async def check_auth_status(user_id: str, oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)):
    """
    Check if user is authenticated with Google

    Args:
        user_id: Unique user identifier

    Returns:
        Authentication status
    """
    credentials = oauth_manager.get_valid_credentials(user_id)
    is_authenticated = credentials is not None

    if is_authenticated:
        try:
            user_info = oauth_manager.get_user_info(credentials)
            return {
                "authenticated": True,
                "email": user_info.get("email"),
                "name": user_info.get("name")
            }
        except Exception as e:
            return {
                "authenticated": False,
                "error": f"Failed to get user info: {str(e)}"
            }
    else:
        return {
            "authenticated": False,
            "message": "User not authenticated with Google"
        }


@router.get("/calendars/{user_id}")
async def list_calendars(
    user_id: str,
    calendar_manager: GoogleCalendarManager = Depends(get_calendar_manager)
) -> List[Dict[str, Any]]:
    """
    List all calendars accessible to the user

    Args:
        user_id: Unique user identifier

    Returns:
        List of calendar objects
    """
    try:
        calendars = calendar_manager.list_calendars()
        return calendars
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list calendars: {str(e)}")


@router.get("/events/{user_id}")
async def get_upcoming_events(
    user_id: str,
    calendar_id: str = Query("primary", description="Calendar ID"),
    max_results: int = Query(10, description="Maximum number of events"),
    days_ahead: int = Query(7, description="Days to look ahead"),
    calendar_manager: GoogleCalendarManager = Depends(get_calendar_manager)
) -> Dict[str, Any]:
    """
    Get upcoming events from user's calendar

    Args:
        user_id: Unique user identifier
        calendar_id: Calendar ID (default: primary)
        max_results: Maximum events to return
        days_ahead: Days to look ahead

    Returns:
        Events data with analysis
    """
    try:
        events = calendar_manager.get_upcoming_events(
            calendar_id=calendar_id,
            max_results=max_results,
            days_ahead=days_ahead
        )

        # Analyze occasions for outfit recommendations
        occasions = calendar_manager.analyze_occasions(days_ahead=days_ahead)

        return {
            "events": events,
            "occasions": occasions,
            "calendar_id": calendar_id,
            "count": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")


@router.get("/events/{user_id}/date")
async def get_events_for_date(
    user_id: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    calendar_id: str = Query("primary", description="Calendar ID"),
    calendar_manager: GoogleCalendarManager = Depends(get_calendar_manager)
) -> List[Dict[str, Any]]:
    """
    Get all events for a specific date

    Args:
        user_id: Unique user identifier
        date: Date string (YYYY-MM-DD)
        calendar_id: Calendar ID (default: primary)

    Returns:
        List of events for the date
    """
    try:
        # Parse date
        target_date = datetime.fromisoformat(date)

        events = calendar_manager.get_events_for_date(target_date, calendar_id)
        return events
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get events for date: {str(e)}")


@router.post("/events/{user_id}")
async def create_event(
    user_id: str,
    summary: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_id: str = "primary",
    calendar_manager: GoogleCalendarManager = Depends(get_calendar_manager)
) -> Dict[str, Any]:
    """
    Create a new calendar event

    Args:
        user_id: Unique user identifier
        summary: Event title
        start_time: Start time (ISO format)
        end_time: End time (ISO format)
        description: Event description
        location: Event location
        calendar_id: Calendar ID (default: primary)

    Returns:
        Created event data
    """
    try:
        # Parse datetime strings
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

        event = calendar_manager.create_event(
            summary=summary,
            start_time=start_dt,
            end_time=end_dt,
            description=description or "",
            location=location or "",
            calendar_id=calendar_id
        )

        if event:
            return event
        else:
            raise HTTPException(status_code=500, detail="Failed to create event")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


@router.get("/outfit-context/{user_id}")
async def get_outfit_recommendations_context(
    user_id: str,
    days_ahead: int = Query(7, description="Days to analyze"),
    calendar_manager: GoogleCalendarManager = Depends(get_calendar_manager)
) -> Dict[str, Any]:
    """
    Get outfit recommendation context based on calendar events

    Args:
        user_id: Unique user identifier
        days_ahead: Days to analyze

    Returns:
        Context for outfit recommendations
    """
    try:
        context = calendar_manager.get_outfit_recommendations_context()
        occasions = calendar_manager.analyze_occasions(days_ahead=days_ahead)

        return {
            "context": context,
            "occasions": occasions,
            "analysis_period_days": days_ahead
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze calendar: {str(e)}")


@router.get("/auth/callback")
async def handle_oauth_web_callback(
    code: str = Query(..., description="Authorization code"),
    state: Optional[str] = Query(None, description="State parameter"),
    error: Optional[str] = Query(None, description="Error parameter")
):
    """
    Handle OAuth callback from Google (web redirect)

    This endpoint is called by Google after user authorization.
    It should redirect back to the frontend with the authorization code.

    Args:
        code: Authorization code from Google
        state: State parameter (contains user_id)
        error: Error parameter if authorization failed

    Returns:
        Redirect to frontend with results
    """
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')

    if error:
        # Redirect with error
        return RedirectResponse(
            url=f"{frontend_url}/calendar/auth/callback?error={error}",
            status_code=302
        )

    if not code:
        return RedirectResponse(
            url=f"{frontend_url}/calendar/auth/callback?error=no_code",
            status_code=302
        )

    # Redirect to frontend with the authorization code
    # The frontend will then call the backend API to exchange the code for tokens
    redirect_url = f"{frontend_url}/calendar/auth/callback?code={code}"
    if state:
        redirect_url += f"&state={state}"

    return RedirectResponse(url=redirect_url, status_code=302)


@router.post("/auth/exchange-code/{user_id}")
async def exchange_authorization_code(
    user_id: str,
    code: str = Query(..., description="Authorization code"),
    oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)
):
    """
    Exchange authorization code for access and refresh tokens

    Args:
        user_id: Unique user identifier
        code: Authorization code from Google OAuth flow

    Returns:
        Success message
    """
    try:
        # Create authorization response URL
        authorization_response = f"{oauth_manager.redirect_uri}?code={code}"

        # Get the flow
        flow = oauth_manager.initiate_oauth_flow()

        # Exchange code for tokens
        credentials = oauth_manager.exchange_code_for_tokens(flow, authorization_response)

        # Save credentials
        oauth_manager.save_credentials(user_id, credentials)

        return {
            "message": "Authentication successful",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to exchange code: {str(e)}")


@router.delete("/auth/{user_id}")
async def revoke_google_auth(user_id: str, oauth_manager: GoogleOAuthManager = Depends(get_oauth_manager)):
    """
    Revoke Google authentication for a user

    Args:
        user_id: Unique user identifier

    Returns:
        Success message
    """
    try:
        oauth_manager.revoke_credentials(user_id)
        return {
            "message": "Google authentication revoked successfully",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke authentication: {str(e)}")