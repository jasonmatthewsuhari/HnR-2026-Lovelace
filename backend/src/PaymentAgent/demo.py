"""
Payment Agent Interactive Demo

Run this to see the Payment Agent in action!
Demonstrates all key features with a simulated shopping experience.
"""

import asyncio
import os
import time
from typing import Optional
from dotenv import load_dotenv

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a fancy header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_step(number: int, text: str):
    """Print a step marker"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[Step {number}]{Colors.END} {Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*50}{Colors.END}")

def print_user(text: str):
    """Print user message"""
    print(f"{Colors.GREEN}👤 User:{Colors.END} {text}")

def print_agent(text: str):
    """Print agent response"""
    print(f"{Colors.CYAN}🤖 Agent:{Colors.END} {text}")

def print_system(text: str):
    """Print system message"""
    print(f"{Colors.YELLOW}⚙️  System:{Colors.END} {text}")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def typing_effect(text: str, delay: float = 0.03):
    """Simulate typing effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

async def simulate_thinking(duration: float = 1.0):
    """Simulate agent thinking"""
    print(f"{Colors.YELLOW}💭 Thinking", end='', flush=True)
    for _ in range(3):
        await asyncio.sleep(duration / 3)
        print(".", end='', flush=True)
    print(f"{Colors.END}")


async def demo_1_introduction():
    """Demo 1: Introduction and Setup"""
    print_header("🎬 DEMO 1: Introduction to Payment Agent")
    
    print(f"{Colors.BOLD}What is the Payment Agent?{Colors.END}")
    print("""
The Payment Agent is an AI-powered shopping assistant that uses:
• Gemini AI for natural language understanding
• Universal Checkout Protocol (UCP) for standardized checkout
• Stripe for secure payments with Shared Payment Tokens
• Playwright for browser automation fallback

It integrates with Lovelace features like:
• 📅 Calendar sync (event-aware shopping)
• 👗 Wardrobe database (avoid duplicates)
• 🎭 Virtual try-on (try before you buy)
• 📸 Photobooth (celebrate purchases!)
""")
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")


async def demo_2_chat_interface():
    """Demo 2: Chat Interface"""
    print_header("🎬 DEMO 2: AI-Powered Conversation")
    
    print_info("The agent understands natural language and context")
    print()
    
    conversations = [
        {
            "user": "Hi! I have a wedding to attend next Saturday",
            "agent": "How exciting! A wedding is a special occasion. I'd be happy to help you find the perfect outfit. What's your style preference? Are you thinking elegant, classic, modern, or something else?"
        },
        {
            "user": "I prefer elegant dresses, maybe in navy blue or burgundy",
            "agent": "Excellent choices! Navy blue and burgundy are sophisticated colors perfect for a wedding. Let me search for elegant dresses in those colors for you..."
        },
        {
            "user": "Show me options under $150",
            "agent": "I found 5 beautiful elegant dresses in navy and burgundy under $150:\n\n1. Navy Silk Evening Dress - $129.99\n2. Burgundy Lace Midi Dress - $119.99\n3. Navy Chiffon A-Line Dress - $139.99\n4. Burgundy Velvet Cocktail Dress - $149.99\n5. Navy Satin Wrap Dress - $134.99\n\nWould you like to see details or try any of these on virtually?"
        },
        {
            "user": "The second one looks perfect! Add it to my cart",
            "agent": "Great choice! The Burgundy Lace Midi Dress ($119.99) has been added to your cart. It's a beautiful piece that will look stunning at the wedding!\n\nWould you like to:\n• Add matching accessories\n• Try it on virtually first\n• Proceed to checkout"
        }
    ]
    
    for i, conv in enumerate(conversations, 1):
        print()
        print_user(conv["user"])
        await simulate_thinking(0.8)
        print_agent(conv["agent"])
        await asyncio.sleep(1.5)
    
    print()
    print_success("Natural conversation completed!")
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")


async def demo_3_product_search():
    """Demo 3: Product Search"""
    print_header("🎬 DEMO 3: Intelligent Product Search")
    
    print_step(1, "Searching Stripe Product Catalog")
    print_user("Search for summer dresses")
    await simulate_thinking()
    
    # Simulated search results
    products = [
        {"id": "prod_001", "name": "Floral Sundress", "price": 79.99, "image": "dress1.jpg"},
        {"id": "prod_002", "name": "White Linen Dress", "price": 89.99, "image": "dress2.jpg"},
        {"id": "prod_003", "name": "Blue Maxi Dress", "price": 99.99, "image": "dress3.jpg"},
        {"id": "prod_004", "name": "Yellow A-Line Dress", "price": 69.99, "image": "dress4.jpg"},
        {"id": "prod_005", "name": "Green Wrap Dress", "price": 84.99, "image": "dress5.jpg"},
    ]
    
    print_success(f"Found {len(products)} products:\n")
    for i, product in enumerate(products, 1):
        print(f"   {i}. {Colors.BOLD}{product['name']}{Colors.END}")
        print(f"      💰 ${product['price']}")
        print(f"      🆔 {product['id']}")
        print()
    
    print_step(2, "Context-Aware Filtering")
    print_info("Agent checks your wardrobe to avoid duplicates...")
    await simulate_thinking()
    
    print_system("Checking existing wardrobe...")
    await asyncio.sleep(1)
    print_success("You already have 2 floral dresses - suggesting alternatives")
    print_info("Filtering by your style preferences: elegant, sophisticated")
    
    print()
    print_agent("Based on your wardrobe and preferences, I'd recommend the White Linen Dress or Blue Maxi Dress!")
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")


async def demo_4_cart_management():
    """Demo 4: Cart Management"""
    print_header("🎬 DEMO 4: Shopping Cart Management")
    
    print_step(1, "Adding Items to Cart")
    
    cart_items = [
        {"name": "White Linen Dress", "price": 89.99, "qty": 1},
        {"name": "Pearl Necklace", "price": 45.00, "qty": 1},
        {"name": "Nude Heels", "price": 79.99, "qty": 1},
    ]
    
    for item in cart_items:
        print_user(f"Add {item['name']} to cart")
        await simulate_thinking(0.5)
        print_success(f"Added {item['name']} (${item['price']}) x{item['qty']}")
        await asyncio.sleep(0.5)
    
    print()
    print_step(2, "Viewing Cart")
    print_agent("Here's your shopping cart:\n")
    
    total = 0
    for i, item in enumerate(cart_items, 1):
        subtotal = item['price'] * item['qty']
        total += subtotal
        print(f"   {i}. {Colors.BOLD}{item['name']}{Colors.END}")
        print(f"      ${item['price']} x {item['qty']} = ${subtotal:.2f}")
        print()
    
    print(f"   {Colors.BOLD}{'─'*40}{Colors.END}")
    print(f"   {Colors.BOLD}Subtotal: ${total:.2f}{Colors.END}")
    print(f"   {Colors.YELLOW}(Tax and shipping calculated at checkout){Colors.END}")
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")


async def demo_5_ucp_discovery():
    """Demo 5: UCP Protocol Discovery"""
    print_header("🎬 DEMO 5: Universal Checkout Protocol Discovery")
    
    print_info("The agent checks if merchants support UCP for seamless checkout\n")
    
    merchants = [
        {
            "url": "https://fashion-boutique.example.com",
            "name": "Fashion Boutique",
            "supports_ucp": True,
            "version": "1.0",
            "features": ["realtime_tax", "shipping_options", "gift_wrapping"]
        },
        {
            "url": "https://legacy-shop.example.com",
            "name": "Legacy Shop",
            "supports_ucp": False,
        },
        {
            "url": "https://modern-store.example.com",
            "name": "Modern Store",
            "supports_ucp": True,
            "version": "1.1",
            "features": ["realtime_tax", "shipping_options", "subscription_support"]
        }
    ]
    
    for i, merchant in enumerate(merchants, 1):
        print_step(i, f"Checking {merchant['name']}")
        print_system(f"GET {merchant['url']}/.well-known/ucp")
        await simulate_thinking(0.8)
        
        if merchant['supports_ucp']:
            print_success(f"UCP Supported! (v{merchant['version']})")
            print(f"   {Colors.GREEN}✓{Colors.END} Features: {', '.join(merchant['features'])}")
            print(f"   {Colors.GREEN}✓{Colors.END} Will use direct UCP checkout")
        else:
            print_error("UCP Not Supported")
            print(f"   {Colors.YELLOW}→{Colors.END} Will use browser automation fallback")
        
        print()
        await asyncio.sleep(1)
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")


async def demo_6_checkout_flow():
    """Demo 6: Complete Checkout Flow"""
    print_header("🎬 DEMO 6: UCP Checkout Flow")
    
    print_step(1, "Creating Checkout Session")
    print_user("Proceed to checkout")
    await simulate_thinking()
    
    print_system("Initializing UCP client...")
    await asyncio.sleep(0.5)
    print_system("POST /ucp/checkout")
    await asyncio.sleep(0.5)
    
    print_success("Checkout session created!\n")
    checkout_data = {
        "id": "checkout_abc123xyz",
        "subtotal": 214.98,
        "tax": 17.20,
        "shipping": 8.99,
        "total": 241.17
    }
    
    print(f"   Checkout ID: {Colors.BOLD}{checkout_data['id']}{Colors.END}")
    print(f"   Subtotal: ${checkout_data['subtotal']:.2f}")
    print(f"   Tax: ${checkout_data['tax']:.2f}")
    print(f"   Shipping: ${checkout_data['shipping']:.2f}")
    print(f"   {Colors.BOLD}Total: ${checkout_data['total']:.2f}{Colors.END}")
    
    print()
    print_step(2, "Showing Shipping Options")
    await simulate_thinking(0.5)
    
    print_agent("Available shipping options:\n")
    shipping_options = [
        {"id": "standard", "name": "Standard (5-7 days)", "price": 8.99},
        {"id": "express", "name": "Express (2-3 days)", "price": 14.99},
        {"id": "overnight", "name": "Overnight", "price": 24.99},
    ]
    
    for i, option in enumerate(shipping_options, 1):
        print(f"   {i}. {option['name']} - ${option['price']:.2f}")
    
    print()
    print_user("Select standard shipping")
    await simulate_thinking(0.5)
    print_system("PATCH /ucp/checkout/checkout_abc123xyz")
    print_success("Shipping option updated!")
    
    print()
    print_step(3, "Generating Shared Payment Token")
    await simulate_thinking()
    
    print_system("Requesting SPT from Stripe...")
    await asyncio.sleep(1)
    print_success("Shared Payment Token generated!")
    print(f"   Token: {Colors.BOLD}spt_*********************xyz{Colors.END}")
    print(f"   {Colors.YELLOW}ℹ️  Token is one-time use, expires in 5 minutes{Colors.END}")
    
    print()
    print_step(4, "User Confirmation")
    print_agent(f"Ready to complete your purchase:\n")
    print(f"   {Colors.BOLD}Total: ${checkout_data['total']:.2f}{Colors.END}")
    print(f"   Payment: Visa ending in 4242")
    print(f"   Shipping: Standard (5-7 days)")
    print()
    
    print_user("Confirm purchase")
    await simulate_thinking()
    
    print()
    print_step(5, "Completing Checkout")
    print_system("POST /ucp/checkout/checkout_abc123xyz/complete")
    await asyncio.sleep(1)
    
    print()
    print_success("🎉 ORDER CONFIRMED! 🎉\n")
    print(f"   Order Number: {Colors.BOLD}#WED-2026-0125{Colors.END}")
    print(f"   Total: ${checkout_data['total']:.2f}")
    print(f"   Estimated Delivery: Saturday, Jan 25")
    print(f"   Tracking: Will be sent to your email")
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")


async def demo_7_browser_fallback():
    """Demo 7: Browser Automation Fallback"""
    print_header("🎬 DEMO 7: Browser Automation Fallback")
    
    print_info("For merchants without UCP, the agent uses browser automation\n")
    
    print_step(1, "Detecting Non-UCP Merchant")
    print_system("GET https://legacy-shop.com/.well-known/ucp")
    await simulate_thinking()
    print_error("404 Not Found - UCP not supported")
    print_system("Initiating browser automation fallback...")
    
    print()
    print_step(2, "Launching Headless Browser")
    await asyncio.sleep(0.5)
    print_success("Chromium browser launched (headless mode)")
    await asyncio.sleep(0.5)
    print_system("Navigating to https://legacy-shop.com")
    
    print()
    print_step(3, "Automating Checkout Process")
    
    automation_steps = [
        "Finding product page...",
        "Clicking 'Add to Cart' button...",
        "Navigating to cart...",
        "Clicking 'Checkout' button...",
        "Filling email: user@example.com",
        "Filling shipping address...",
        "Selecting saved payment method...",
        "Reviewing order total: $241.17",
        "Clicking 'Place Order'...",
        "Waiting for confirmation...",
    ]
    
    for step in automation_steps:
        print(f"   {Colors.YELLOW}→{Colors.END} {step}")
        await asyncio.sleep(0.6)
    
    print()
    await asyncio.sleep(1)
    print_success("Order completed successfully!")
    print(f"   Order Number: {Colors.BOLD}#LSH-2026-1234{Colors.END}")
    print(f"   Screenshot saved: order_confirmation.png")
    
    print()
    print_info("Browser automation works with most checkout flows")
    print_info("Uses saved payment methods for security")
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")


async def demo_8_integration():
    """Demo 8: Integration with Lovelace Features"""
    print_header("🎬 DEMO 8: Lovelace Integration")
    
    print_info("Payment Agent works seamlessly with other Lovelace features\n")
    
    integrations = [
        {
            "feature": "📅 Calendar Sync",
            "description": "Agent checks your calendar for upcoming events",
            "example": "You have a wedding on Saturday → suggests elegant dresses"
        },
        {
            "feature": "👗 Wardrobe Database",
            "description": "Agent knows what you already own",
            "example": "You have 3 blue dresses → suggests other colors"
        },
        {
            "feature": "🎭 Virtual Try-On",
            "description": "Try clothes before buying",
            "example": "See how the dress looks on you virtually"
        },
        {
            "feature": "📸 Photobooth",
            "description": "Celebrate purchases with your virtual boyfriend",
            "example": "Take a celebration photo after order confirmation"
        },
        {
            "feature": "🎨 Product to 3D",
            "description": "Convert purchases to 3D models",
            "example": "Add 3D model of purchased dress to your wardrobe"
        }
    ]
    
    for i, integration in enumerate(integrations, 1):
        print_step(i, integration["feature"])
        print(f"   {Colors.BOLD}What:{Colors.END} {integration['description']}")
        print(f"   {Colors.BOLD}Example:{Colors.END} {integration['example']}")
        print()
        await asyncio.sleep(1)
    
    print_success("All integrations working seamlessly!")
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")


async def demo_9_complete_scenario():
    """Demo 9: Complete Real-World Scenario"""
    print_header("🎬 DEMO 9: Complete Shopping Journey")
    
    print_info("Let's see a complete end-to-end shopping experience\n")
    
    scenario = [
        ("📅", "Monday: Calendar sync detects wedding event on Saturday"),
        ("💬", "Virtual boyfriend: 'You have a wedding! Need an outfit?'"),
        ("🔍", "User: 'Yes, show me elegant dresses'"),
        ("🤖", "Agent searches products, filters by wardrobe & preferences"),
        ("👗", "Shows 5 curated options in navy and burgundy"),
        ("🎭", "User tries on 2 dresses virtually"),
        ("💖", "User loves the burgundy lace dress"),
        ("🛒", "Agent adds dress + matching accessories to cart"),
        ("💳", "Agent creates checkout session (UCP)"),
        ("🔐", "Generates Shared Payment Token"),
        ("✅", "User confirms purchase"),
        ("📦", "Order completed! Tracking sent to email"),
        ("📸", "Takes celebration photo with virtual boyfriend"),
        ("🎨", "Converts dress to 3D model for wardrobe"),
        ("✨", "Complete! Ready for the wedding!"),
    ]
    
    for emoji, description in scenario:
        print(f"{emoji}  {description}")
        await asyncio.sleep(0.8)
    
    print()
    print_success("🎉 Complete shopping journey from calendar to celebration! 🎉")
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")


async def demo_10_api_examples():
    """Demo 10: API Usage Examples"""
    print_header("🎬 DEMO 10: REST API Examples")
    
    print_info("All features available via REST API\n")
    
    api_examples = [
        {
            "title": "Chat with Agent",
            "method": "POST",
            "endpoint": "/payment-agent/chat",
            "body": {
                "message": "Show me summer dresses",
                "context": {"calendar_events": [], "wardrobe": []}
            }
        },
        {
            "title": "Search Products",
            "method": "POST",
            "endpoint": "/payment-agent/search-products",
            "body": {
                "query": "blue jeans",
                "limit": 10
            }
        },
        {
            "title": "Add to Cart",
            "method": "POST",
            "endpoint": "/payment-agent/cart/add",
            "body": {
                "product_id": "prod_123",
                "quantity": 1
            }
        },
        {
            "title": "Create Checkout",
            "method": "POST",
            "endpoint": "/payment-agent/checkout/create",
            "body": {
                "merchant_url": "https://shop.example.com",
                "buyer_email": "user@example.com"
            }
        }
    ]
    
    for i, example in enumerate(api_examples, 1):
        print_step(i, example["title"])
        print(f"   {Colors.BOLD}{example['method']}{Colors.END} {example['endpoint']}")
        print(f"   Body: {Colors.YELLOW}{example['body']}{Colors.END}")
        print()
        await asyncio.sleep(1)
    
    print_info("Full API documentation at: http://localhost:8000/docs")
    
    input(f"\n{Colors.YELLOW}Press Enter to finish...{Colors.END}")


async def main():
    """Run all demos"""
    load_dotenv()
    
    # Set UTF-8 encoding for Windows
    import sys
    if sys.platform == "win32":
        try:
            import codecs
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        except:
            pass
    
    # ASCII Art Title
    print(f"""
{Colors.BOLD}{Colors.CYAN}
===================================================================
                                                                   
         PAYMENT AGENT - INTERACTIVE DEMO                         
                                                                   
      Agentic Commerce with Universal Checkout Protocol        
                                                                   
===================================================================
{Colors.END}
""")
    
    print(f"{Colors.BOLD}Welcome to the Payment Agent Demo!{Colors.END}")
    print()
    print("This interactive demo showcases:")
    print("  • AI-powered shopping conversations")
    print("  • Intelligent product search")
    print("  • Universal Checkout Protocol (UCP)")
    print("  • Secure payment with Shared Payment Tokens")
    print("  • Browser automation fallback")
    print("  • Integration with Lovelace features")
    print()
    
    input(f"{Colors.YELLOW}Press Enter to start the demo...{Colors.END}")
    
    demos = [
        ("Introduction", demo_1_introduction),
        ("AI Chat Interface", demo_2_chat_interface),
        ("Product Search", demo_3_product_search),
        ("Cart Management", demo_4_cart_management),
        ("UCP Discovery", demo_5_ucp_discovery),
        ("Checkout Flow", demo_6_checkout_flow),
        ("Browser Fallback", demo_7_browser_fallback),
        ("Lovelace Integration", demo_8_integration),
        ("Complete Scenario", demo_9_complete_scenario),
        ("API Examples", demo_10_api_examples),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            await demo_func()
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Demo interrupted by user{Colors.END}")
            break
        except Exception as e:
            print(f"\n{Colors.RED}Error in {name}: {str(e)}{Colors.END}")
            import traceback
            traceback.print_exc()
    
    # Final Summary
    print_header("DEMO COMPLETE!")
    
    print(f"""
{Colors.BOLD}What You've Seen:{Colors.END}

- AI-powered conversational shopping
- Intelligent product search with context
- Universal Checkout Protocol integration
- Secure payments with Shared Payment Tokens
- Browser automation for legacy merchants
- Full integration with Lovelace features
- Complete REST API

{Colors.BOLD}Next Steps:{Colors.END}

1. Test Setup:      python test_setup.py
2. Start Server:    cd ../.. && python main.py
3. API Docs:        http://localhost:8000/docs
4. Integration:     See INTEGRATION.md
5. Documentation:   See README.md

{Colors.BOLD}Quick Start Commands:{Colors.END}

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Add to backend/.env
GEMINI_API_KEY=your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here

# Run this demo again
python demo.py

{Colors.BOLD}Thank you for watching the demo!{Colors.END}
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo terminated by user. Goodbye!{Colors.END}")
