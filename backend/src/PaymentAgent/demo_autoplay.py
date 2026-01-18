"""
Payment Agent Auto-Play Demo

A self-running demo that showcases all Payment Agent features.
No interaction required - just sit back and watch!
"""

import asyncio
import sys
import time

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    except:
        pass

# Color codes
class C:
    H = '\033[95m'  # Header
    B = '\033[94m'  # Blue
    C = '\033[96m'  # Cyan
    G = '\033[92m'  # Green
    Y = '\033[93m'  # Yellow
    R = '\033[91m'  # Red
    E = '\033[0m'   # End
    BOLD = '\033[1m'

def p(text, color='', delay=0.03):
    """Print with optional color and typing effect"""
    for char in (color + text + C.E):
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

async def wait(s=1.0):
    """Async wait"""
    await asyncio.sleep(s)

async def main():
    print(f"""
{C.BOLD}{C.C}
===================================================================
                                                                   
         PAYMENT AGENT - AUTO-PLAY DEMO                         
                                                                   
      Agentic Commerce with Universal Checkout Protocol        
                                                                   
===================================================================
{C.E}
""")
    
    print(f"{C.BOLD}A complete AI-powered shopping system for Lovelace{C.E}\n")
    await wait(2)
    
    # ===== DEMO 1: INTRODUCTION =====
    print(f"\n{C.BOLD}{C.C}{'='*70}{C.E}")
    print(f"{C.BOLD}{C.C}{'PART 1: INTRODUCTION'.center(70)}{C.E}")
    print(f"{C.BOLD}{C.C}{'='*70}{C.E}\n")
    await wait(1)
    
    p(f"{C.BOLD}What is the Payment Agent?{C.E}", C.C)
    print("""
The Payment Agent is an AI shopping assistant that combines:
  - Gemini AI for natural language understanding
  - Universal Checkout Protocol (UCP) for standardized checkout
  - Stripe for secure payments
  - Playwright for browser automation fallback
""")
    await wait(3)
    
    # ===== DEMO 2: CONVERSATION =====
    print(f"\n{C.BOLD}{C.C}{'='*70}{C.E}")
    print(f"{C.BOLD}{C.C}{'PART 2: AI-POWERED CONVERSATION'.center(70)}{C.E}")
    print(f"{C.BOLD}{C.C}{'='*70}{C.E}\n")
    await wait(1)
    
    conversations = [
        ("User", "Hi! I have a wedding to attend next Saturday", C.G),
        ("Agent", "How exciting! I'd be happy to help you find the perfect outfit. What's your style preference?", C.C),
        ("User", "I prefer elegant dresses, maybe in navy blue or burgundy", C.G),
        ("Agent", "Excellent choices! Let me search for elegant dresses in those colors...", C.C),
        ("User", "Show me options under $150", C.G),
        ("Agent", "I found 5 beautiful dresses:\n  1. Navy Silk Evening Dress - $129.99\n  2. Burgundy Lace Midi Dress - $119.99\n  3. Navy Chiffon A-Line Dress - $139.99", C.C),
        ("User", "The second one looks perfect! Add it to my cart", C.G),
        ("Agent", "Great choice! The Burgundy Lace Midi Dress has been added to your cart!", C.C),
    ]
    
    for speaker, message, color in conversations:
        print(f"\n{color}{speaker}:{C.E} {message}")
        await wait(2)
    
    await wait(1)
    print(f"\n{C.G}✓ Natural conversation completed!{C.E}")
    await wait(2)
    
    # ===== DEMO 3: PRODUCT SEARCH =====
    print(f"\n{C.BOLD}{C.C}{'='*70}{C.E}")
    print(f"{C.BOLD}{C.C}{'PART 3: INTELLIGENT PRODUCT SEARCH'.center(70)}{C.E}")
    print(f"{C.BOLD}{C.C}{'='*70}{C.E}\n")
    await wait(1)
    
    print(f"{C.Y}Searching Stripe catalog...{C.E}")
    await wait(1)
    
    print(f"\n{C.G}✓ Found 5 products:{C.E}\n")
    products = [
        "1. Floral Sundress - $79.99",
        "2. White Linen Dress - $89.99",
        "3. Blue Maxi Dress - $99.99",
        "4. Yellow A-Line Dress - $69.99",
        "5. Green Wrap Dress - $84.99"
    ]
    
    for product in products:
        print(f"   {product}")
        await wait(0.5)
    
    await wait(1)
    print(f"\n{C.Y}Checking your wardrobe to avoid duplicates...{C.E}")
    await wait(1)
    print(f"{C.G}✓ You already have 2 floral dresses - suggesting alternatives{C.E}")
    await wait(2)
    
    # ===== DEMO 4: CART =====
    print(f"\n{C.BOLD}{C.C}{'='*70}{C.E}")
    print(f"{C.BOLD}{C.C}{'PART 4: CART MANAGEMENT'.center(70)}{C.E}")
    print(f"{C.BOLD}{C.C}{'='*70}{C.E}\n")
    await wait(1)
    
    print(f"{C.Y}Adding items to cart...{C.E}\n")
    
    cart = [
        "Burgundy Lace Dress - $119.99",
        "Pearl Necklace - $45.00",
        "Nude Heels - $79.99"
    ]
    
    for item in cart:
        print(f"{C.G}✓{C.E} Added {item}")
        await wait(0.8)
    
    await wait(1)
    print(f"\n{C.BOLD}Cart Summary:{C.E}")
    print("─" * 40)
    for i, item in enumerate(cart, 1):
        print(f"  {i}. {item}")
    print("─" * 40)
    print(f"  {C.BOLD}Subtotal: $244.98{C.E}")
    await wait(2)
    
    # ===== DEMO 5: UCP DISCOVERY =====
    print(f"\n{C.BOLD}{C.C}{'='*70}{C.E}")
    print(f"{C.BOLD}{C.C}{'PART 5: UNIVERSAL CHECKOUT PROTOCOL'.center(70)}{C.E}")
    print(f"{C.BOLD}{C.C}{'='*70}{C.E}\n")
    await wait(1)
    
    print(f"{C.Y}Checking merchant UCP support...{C.E}")
    await wait(1)
    print(f"{C.Y}GET https://fashion-boutique.com/.well-known/ucp{C.E}")
    await wait(1)
    print(f"{C.G}✓ UCP Supported! (v1.0){C.E}")
    print(f"  Features: realtime_tax, shipping_options, gift_wrapping")
    await wait(2)
    
    # ===== DEMO 6: CHECKOUT =====
    print(f"\n{C.BOLD}{C.C}{'='*70}{C.E}")
    print(f"{C.BOLD}{C.C}{'PART 6: SECURE CHECKOUT'.center(70)}{C.E}")
    print(f"{C.BOLD}{C.C}{'='*70}{C.E}\n")
    await wait(1)
    
    print(f"{C.Y}[1/4] Creating checkout session...{C.E}")
    await wait(1)
    print(f"{C.G}✓ Checkout created: checkout_abc123{C.E}\n")
    
    print("  Subtotal: $244.98")
    print("  Tax:      $19.60")
    print("  Shipping: $8.99")
    print(f"  {C.BOLD}Total:    $273.57{C.E}")
    await wait(2)
    
    print(f"\n{C.Y}[2/4] Selecting shipping option...{C.E}")
    await wait(1)
    print(f"{C.G}✓ Standard shipping selected (5-7 days){C.E}")
    await wait(1)
    
    print(f"\n{C.Y}[3/4] Generating Shared Payment Token...{C.E}")
    await wait(1)
    print(f"{C.G}✓ SPT generated: spt_*********************xyz{C.E}")
    print(f"  {C.Y}(One-time use, expires in 5 minutes){C.E}")
    await wait(2)
    
    print(f"\n{C.Y}[4/4] Completing checkout...{C.E}")
    await wait(1.5)
    
    print(f"\n{C.BOLD}{C.G}{'='*70}{C.E}")
    print(f"{C.BOLD}{C.G}{'ORDER CONFIRMED!'.center(70)}{C.E}")
    print(f"{C.BOLD}{C.G}{'='*70}{C.E}\n")
    
    print(f"  Order Number: {C.BOLD}#WED-2026-0125{C.E}")
    print(f"  Total: $273.57")
    print(f"  Estimated Delivery: Saturday, Jan 25")
    await wait(3)
    
    # ===== DEMO 7: INTEGRATION =====
    print(f"\n{C.BOLD}{C.C}{'='*70}{C.E}")
    print(f"{C.BOLD}{C.C}{'PART 7: LOVELACE INTEGRATION'.center(70)}{C.E}")
    print(f"{C.BOLD}{C.C}{'='*70}{C.E}\n")
    await wait(1)
    
    integrations = [
        ("Calendar Sync", "Checks your events to suggest appropriate outfits"),
        ("Wardrobe Database", "Avoids suggesting items you already own"),
        ("Virtual Try-On", "Try clothes before buying them"),
        ("Photobooth", "Celebrate purchases with your virtual boyfriend"),
        ("Product to 3D", "Converts purchases to 3D models for your wardrobe")
    ]
    
    for feature, desc in integrations:
        print(f"{C.G}✓{C.E} {C.BOLD}{feature}{C.E}: {desc}")
        await wait(1)
    
    await wait(2)
    
    # ===== DEMO 8: COMPLETE SCENARIO =====
    print(f"\n{C.BOLD}{C.C}{'='*70}{C.E}")
    print(f"{C.BOLD}{C.C}{'PART 8: COMPLETE SHOPPING JOURNEY'.center(70)}{C.E}")
    print(f"{C.BOLD}{C.C}{'='*70}{C.E}\n")
    await wait(1)
    
    journey = [
        "Monday: Calendar detects wedding on Saturday",
        "Virtual boyfriend asks: 'Need an outfit?'",
        "User: 'Yes, show me elegant dresses'",
        "Agent searches & filters by wardrobe preferences",
        "Shows 5 curated options",
        "User tries on 2 dresses virtually",
        "User loves the burgundy lace dress",
        "Agent adds dress + accessories to cart",
        "Agent creates checkout with UCP",
        "Generates Shared Payment Token",
        "User confirms purchase",
        "Order completed! Tracking sent",
        "Takes celebration photo with boyfriend",
        "Converts dress to 3D for wardrobe",
        "Ready for the wedding!"
    ]
    
    for i, step in enumerate(journey, 1):
        print(f"  {i:2d}. {step}")
        await wait(0.6)
    
    await wait(2)
    
    # ===== FINAL SUMMARY =====
    print(f"\n{C.BOLD}{C.C}{'='*70}{C.E}")
    print(f"{C.BOLD}{C.C}{'DEMO COMPLETE!'.center(70)}{C.E}")
    print(f"{C.BOLD}{C.C}{'='*70}{C.E}\n")
    
    print(f"{C.BOLD}What You've Seen:{C.E}\n")
    features = [
        "AI-powered conversational shopping",
        "Intelligent product search",
        "Universal Checkout Protocol",
        "Secure payments with Shared Payment Tokens",
        "Complete Lovelace integration",
        "End-to-end shopping journey"
    ]
    
    for feature in features:
        print(f"  {C.G}✓{C.E} {feature}")
        await wait(0.5)
    
    print(f"\n{C.BOLD}Next Steps:{C.E}\n")
    print("  1. Install: pip install -r requirements.txt")
    print("  2. Configure: Add API keys to backend/.env")
    print("  3. Test: python test_setup.py")
    print("  4. Start: python ../../main.py")
    print("  5. Explore: http://localhost:8000/docs")
    
    print(f"\n{C.BOLD}{C.G}Thank you for watching!{C.E}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\nDemo interrupted. Goodbye!")
