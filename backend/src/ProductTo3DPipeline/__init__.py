"""
Product to 3D Pipeline Module
Converts product images to 3D models with auto-rigging
"""

from .routes import router
from .boyfriend_generator import BoyfriendGenerator

__all__ = ["router", "BoyfriendGenerator"]
