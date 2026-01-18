# Payment Agent - Agentic Commerce Implementation

## Overview

The Payment Agent module implements the **Universal Checkout Protocol (UCP)** by OpenAI and Stripe, enabling autonomous AI-driven shopping experiences. It integrates **Gemini AI** for conversation, **Stripe** for payments, and **Playwright** for browser automation fallback.

## Features

- 🤖 **AI-Powered Shopping**: Gemini AI understands user intent and guides through shopping
- 💳 **Secure Payments**: Shared Payment Tokens (SPT) for secure transactions
- 🔄 **UCP Protocol**: Standardized checkout with compatible merchants
- 🌐 **Browser Fallback**: Playwright automation for non-UCP merchants
- 🛒 **Cart Management**: Full shopping cart functionality
- 📦 **Order Tracking**: Real-time order status updates

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Payment Agent                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐ │
│  │  Gemini AI │  │ UCP Client │  │ Browser Automation   │ │
│  └────────────┘  └────────────┘  └──────────────────────┘ │
│         │               │                    │             │
│         └───────────────┴────────────────────┘             │
│                         │                                   │
│                  ┌──────▼───────┐                          │
│                  │ Stripe Tools │                          │
│                  └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
    │ UCP       │  │ Stripe    │  │ Browser   │
    │ Merchants │  │ Checkout  │  │ Sites     │
    └───────────┘  └───────────┘  └───────────┘
```

## Protocol Flow

### 1. UCP-Compliant Merchants

```
User Request → Agent (Gemini)
     ↓
Discovery: Check .well-known/ucp
     ↓
Create Checkout: POST /ucp/checkout
     ↓
User Reviews: Shipping, taxes, totals
     ↓
Update Checkout: PATCH /ucp/checkout/:id
     ↓
Generate SPT: Stripe SharedPaymentToken
     ↓
Complete: POST /ucp/checkout/:id/complete
     ↓
Order Confirmed ✓
```

### 2. Non-UCP Merchants (Fallback)

```
User Request → Agent (Gemini)
     ↓
Discovery: No UCP support
     ↓
Playwright Launch: Headless browser
     ↓
Navigate & Fill: Automate checkout forms
     ↓
Payment: Use saved methods/tokens
     ↓
Complete: Extract order details
     ↓
Order Confirmed ✓
```

## Installation

1. Install dependencies:

```bash
cd backend/src/PaymentAgent
pip install -r requirements.txt
```

2. Install Playwright browsers:

```bash
playwright install chromium
```

3. Set up environment variables:

```bash
# Copy env.example and fill in your keys
cp ../../env.example ../../.env
```

Add to `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key
STRIPE_SECRET_KEY=sk_test_your_stripe_key
```

## Usage

### Python API

```python
from backend.src.PaymentAgent import PaymentAgent

# Initialize agent
agent = PaymentAgent()

# Chat with agent
response = await agent.chat(
    user_message="I need a new dress for a wedding next week",
    user_context={
        "calendar_events": [...],
        "wardrobe": [...]
    }
)
print(response)

# Search products
products = await agent._search_products(query="red dress", limit=10)

# Add to cart
await agent._add_to_cart(product_id="prod_123", quantity=1)

# Create checkout
checkout = await agent._create_checkout(
    merchant_url="https://shop.example.com",
    buyer_email="user@example.com",
    shipping_address={
        "line1": "123 Main St",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94103",
        "country": "US"
    }
)

# Complete checkout (with user confirmation)
order = await agent._complete_checkout(
    checkout_id=checkout["id"],
    confirm_purchase=True
)
```

### REST API

Start the server:

```bash
cd backend
python main.py
```

#### Endpoints

**Chat with Agent**
```http
POST /payment-agent/chat
Content-Type: application/json

{
  "message": "Show me summer dresses under $100",
  "context": {
    "calendar_events": []
  }
}
```

**Search Products**
```http
POST /payment-agent/search-products
Content-Type: application/json

{
  "query": "blue jeans",
  "limit": 10
}
```

**Add to Cart**
```http
POST /payment-agent/cart/add
Content-Type: application/json

{
  "product_id": "prod_123",
  "quantity": 2,
  "price_id": "price_456"
}
```

**View Cart**
```http
GET /payment-agent/cart
```

**Create Checkout**
```http
POST /payment-agent/checkout/create
Content-Type: application/json

{
  "merchant_url": "https://shop.example.com",
  "buyer_email": "user@example.com",
  "buyer_name": "Jane Doe",
  "shipping_address": {
    "line1": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94103",
    "country": "US"
  }
}
```

**Complete Checkout**
```http
POST /payment-agent/checkout/complete
Content-Type: application/json

{
  "checkout_id": "checkout_123",
  "confirm_purchase": true
}
```

**Check Order Status**
```http
POST /payment-agent/order/status
Content-Type: application/json

{
  "order_id": "order_123"
}
```

**Discover UCP Support**
```http
POST /payment-agent/ucp/discover?merchant_url=https://shop.example.com
```

## Components

### 1. Payment Agent (`payment_agent.py`)

Main orchestrator that:
- Manages conversation with Gemini
- Routes requests to appropriate services
- Maintains session state (cart, checkout)
- Coordinates UCP vs fallback flows

### 2. UCP Client (`ucp_client.py`)

Implements Universal Checkout Protocol:
- `discover()`: Check merchant UCP support via `.well-known/ucp`
- `create_checkout()`: Initialize checkout session
- `update_checkout()`: Modify items, shipping, etc.
- `complete_checkout()`: Finalize with Shared Payment Token
- `cancel_checkout()`: Cancel session

### 3. Stripe Tools (`stripe_tools.py`)

Stripe API integrations:
- `search_products()`: Search product catalog
- `create_checkout_session()`: Legacy Stripe Checkout
- `check_order_status()`: Order tracking
- `create_shared_payment_token()`: Generate SPT for UCP

### 4. Browser Automation (`browser_automation.py`)

Playwright-based fallback:
- Launches headless Chrome
- Navigates merchant sites
- Fills checkout forms
- Handles payment (saved methods only)
- Extracts order confirmation

### 5. FastAPI Routes (`routes.py`)

REST API endpoints for all payment agent functionality.

## Security

### Shared Payment Tokens (SPT)

SPTs are time-limited, one-use credentials:
- Never expose raw payment details
- Scoped to specific merchant and amount
- Generated by Stripe, consumed by merchant
- Automatically expire after use/timeout

### Browser Automation

- **Only** uses saved payment methods or tokens
- **Never** stores raw card data
- Runs in isolated browser context
- Screenshots for debugging (disabled in production)

### Best Practices

1. **User Confirmation**: Always get explicit consent before finalizing purchases
2. **Amount Verification**: Show totals clearly before payment
3. **Secure Storage**: Use encrypted storage for user credentials
4. **Audit Logs**: Log all payment operations
5. **PCI Compliance**: Follow PCI DSS requirements

## Configuration

### Environment Variables

```env
# Required
GEMINI_API_KEY=your_gemini_api_key
STRIPE_SECRET_KEY=sk_test_your_stripe_key

# Optional
PAYMENT_AGENT_ENABLE_BROWSER=true
PAYMENT_AGENT_HEADLESS=true
PAYMENT_AGENT_TIMEOUT=60000
PAYMENT_AGENT_SCREENSHOT_ON_ERROR=false
```

### Agent Configuration

```python
agent = PaymentAgent(
    gemini_api_key="...",
    stripe_api_key="...",
    enable_browser_fallback=True  # Enable Playwright fallback
)
```

## Testing

Run the demo:

```bash
python -m backend.src.PaymentAgent.demo
```

## Integration with Lovelace

The Payment Agent integrates with other Lovelace features:

1. **Calendar Sync**: Check upcoming events to suggest appropriate outfits
2. **Wardrobe DB**: Consider existing wardrobe when recommending
3. **Virtual Boyfriend**: AI avatar guides shopping experience
4. **VTO**: Try on items before purchase

## Limitations

### UCP Availability

- UCP is in private preview (as of Jan 2026)
- Many merchants don't support it yet
- Fallback required for most sites

### Browser Automation

- Site-specific; may break with UI changes
- Payment limited to saved methods
- Requires user interaction for 2FA
- CAPTCHA may block automation

### Stripe Catalog

- Requires products synced to Stripe
- May not reflect real-time inventory
- Limited to Stripe-connected merchants

## Roadmap

- [ ] Multi-merchant cart (aggregate from multiple stores)
- [ ] Price comparison and best deal finding
- [ ] Subscription management
- [ ] Return/refund handling
- [ ] Multi-currency support
- [ ] Voice shopping integration
- [ ] AR try-on before purchase

## References

- [Agentic Commerce Protocol](https://www.agenticcommerce.dev/)
- [Stripe Agentic Commerce Suite](https://stripe.com/blog/agentic-commerce-suite)
- [Stripe UCP Documentation](https://docs.stripe.com/agentic-commerce/protocol)
- [Gemini API](https://ai.google.dev/)
- [Playwright Documentation](https://playwright.dev/)

## Support

For issues or questions:
1. Check existing documentation
2. Review demo script
3. Open an issue on GitHub
4. Contact the Lovelace team

## License

See LICENSE file in repository root.
