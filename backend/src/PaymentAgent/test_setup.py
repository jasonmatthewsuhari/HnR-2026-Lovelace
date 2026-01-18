"""
Test script to verify Payment Agent setup

Run this to verify all components are properly configured.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def print_result(check_name: str, passed: bool, message: str = ""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} - {check_name}")
    if message:
        print(f"       {message}")


def test_environment_variables():
    """Test environment variables"""
    print("\n[1] Testing Environment Variables")
    print("-" * 50)
    
    # Check Gemini API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    print_result(
        "Gemini API Key",
        bool(gemini_key),
        "Set in .env" if gemini_key else "Missing - add GEMINI_API_KEY to .env"
    )
    
    # Check Stripe API key
    stripe_key = os.getenv("STRIPE_SECRET_KEY")
    print_result(
        "Stripe API Key",
        bool(stripe_key),
        "Set in .env" if stripe_key else "Missing - add STRIPE_SECRET_KEY to .env"
    )
    
    return bool(gemini_key and stripe_key)


def test_dependencies():
    """Test required dependencies"""
    print("\n[2] Testing Dependencies")
    print("-" * 50)
    
    all_ok = True
    
    # Test Stripe
    try:
        import stripe
        print_result("Stripe", True, f"Version {stripe.__version__}")
    except ImportError:
        print_result("Stripe", False, "pip install stripe")
        all_ok = False
    
    # Test Gemini
    try:
        import google.generativeai as genai
        print_result("Google Generative AI", True)
    except ImportError:
        print_result("Google Generative AI", False, "pip install google-generativeai")
        all_ok = False
    
    # Test Playwright
    try:
        import playwright
        print_result("Playwright", True)
    except ImportError:
        print_result("Playwright", False, "pip install playwright")
        all_ok = False
    
    # Test aiohttp
    try:
        import aiohttp
        print_result("aiohttp", True)
    except ImportError:
        print_result("aiohttp", False, "pip install aiohttp")
        all_ok = False
    
    # Test Pydantic
    try:
        import pydantic
        print_result("Pydantic", True, f"Version {pydantic.__version__}")
    except ImportError:
        print_result("Pydantic", False, "pip install pydantic")
        all_ok = False
    
    # Test FastAPI
    try:
        import fastapi
        print_result("FastAPI", True, f"Version {fastapi.__version__}")
    except ImportError:
        print_result("FastAPI", False, "pip install fastapi")
        all_ok = False
    
    return all_ok


def test_module_imports():
    """Test Payment Agent module imports"""
    print("\n[3] Testing Module Imports")
    print("-" * 50)
    
    all_ok = True
    
    try:
        from backend.src.PaymentAgent import PaymentAgent
        print_result("PaymentAgent", True)
    except Exception as e:
        print_result("PaymentAgent", False, str(e))
        all_ok = False
    
    try:
        from backend.src.PaymentAgent.stripe_tools import StripeTools
        print_result("StripeTools", True)
    except Exception as e:
        print_result("StripeTools", False, str(e))
        all_ok = False
    
    try:
        from backend.src.PaymentAgent.ucp_client import UCPClient
        print_result("UCPClient", True)
    except Exception as e:
        print_result("UCPClient", False, str(e))
        all_ok = False
    
    try:
        from backend.src.PaymentAgent.browser_automation import BrowserAutomation
        print_result("BrowserAutomation", True)
    except Exception as e:
        print_result("BrowserAutomation", False, str(e))
        all_ok = False
    
    return all_ok


def test_api_connectivity():
    """Test API connectivity (optional)"""
    print("\n[4] Testing API Connectivity (Optional)")
    print("-" * 50)
    
    # Test Gemini API
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "your_gemini_api_key_here":
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            # Don't actually make a call in test
            print_result("Gemini API", True, "API key configured")
        else:
            print_result("Gemini API", False, "Valid API key needed for testing")
    except Exception as e:
        print_result("Gemini API", False, str(e))
    
    # Test Stripe API
    try:
        import stripe
        api_key = os.getenv("STRIPE_SECRET_KEY")
        if api_key and api_key.startswith("sk_"):
            stripe.api_key = api_key
            # Don't actually make a call in test
            print_result("Stripe API", True, "API key configured")
        else:
            print_result("Stripe API", False, "Valid API key needed for testing")
    except Exception as e:
        print_result("Stripe API", False, str(e))


def main():
    """Run all tests"""
    print("=" * 50)
    print("Payment Agent Setup Verification")
    print("=" * 50)
    
    env_ok = test_environment_variables()
    deps_ok = test_dependencies()
    imports_ok = test_module_imports()
    test_api_connectivity()
    
    print("\n" + "=" * 50)
    
    if env_ok and deps_ok and imports_ok:
        print("✓ ALL CHECKS PASSED")
        print("\nYour Payment Agent is ready to use!")
        print("\nNext steps:")
        print("  1. Run demo: python demo.py")
        print("  2. Start server: python ../../main.py")
        print("  3. Test API: curl http://localhost:8000/payment-agent/capabilities")
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before proceeding.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Install Playwright: playwright install chromium")
        print("  - Add API keys to .env file")
        return 1


if __name__ == "__main__":
    sys.exit(main())
