"""
Payment Agent Module

Agentic Commerce implementation with Universal Checkout Protocol (UCP).

Quick Start:
    1. pip install -r requirements.txt
    2. playwright install chromium
    3. Add GEMINI_API_KEY and STRIPE_SECRET_KEY to .env
    4. python test_setup.py
    5. python demo.py

Features:
    - AI-powered shopping with Gemini
    - UCP protocol for standardized checkout
    - Stripe payment processing with SPT
    - Browser automation fallback
    - Full REST API

Example:
    >>> from backend.src.PaymentAgent import PaymentAgent
    >>> agent = PaymentAgent()
    >>> response = await agent.chat("Show me summer dresses under $100")
    >>> print(response)
    "I found 5 beautiful summer dresses in your budget..."

Documentation:
    - README.md - Complete guide
    - QUICKSTART.md - 5-minute setup
    - INTEGRATION.md - Integration with Lovelace
    - SUMMARY.md - Implementation overview

API Endpoints:
    All under /payment-agent/*:
    - POST /chat - Chat with AI
    - POST /search-products - Search catalog
    - POST /cart/add - Add to cart
    - GET /cart - View cart
    - POST /checkout/create - Create checkout
    - POST /checkout/complete - Complete purchase
    - POST /order/status - Track order

Architecture:
    PaymentAgent (orchestrator)
    ├── Gemini AI (conversation)
    ├── StripeTools (payments)
    ├── UCPClient (protocol)
    └── BrowserAutomation (fallback)

Security:
    - Shared Payment Tokens (SPT) for secure transactions
    - User confirmation required
    - PCI DSS compliant architecture
    - Never exposes raw card data

Integration:
    Works with all Lovelace features:
    - Calendar-aware shopping
    - Wardrobe-aware recommendations
    - Virtual try-on before purchase
    - Photobooth celebrations
    - 3D model generation

Author: Lovelace Team
License: See LICENSE
Version: 1.0.0
"""

from .payment_agent import PaymentAgent
from .stripe_tools import StripeTools
from .ucp_client import UCPClient
from .browser_automation import BrowserAutomation

__version__ = "1.0.0"
__all__ = [
    "PaymentAgent",
    "StripeTools", 
    "UCPClient",
    "BrowserAutomation"
]

# Quick access to main class
Agent = PaymentAgent

# Module info
__doc_url__ = "https://github.com/your-org/lovelace/tree/main/backend/src/PaymentAgent"
__author__ = "Lovelace Team"
__license__ = "MIT"
