"""
Voice Agent Routes

FastAPI routes for voice agent functionality.
"""

from fastapi import APIRouter
from .voice_agent import router as voice_agent_router

router = APIRouter()

# Include WebSocket routes
router.include_router(voice_agent_router)

__all__ = ['router']
