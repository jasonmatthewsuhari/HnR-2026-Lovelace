# Payment Agent Integration Guide

## Overview

The Payment Agent is now fully integrated into Lovelace! This guide shows how to use it with the existing features.

## Architecture Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    Lovelace Frontend                        │
└────────────┬────────────────────────────────────────────────┘
             │
             │ REST API
             │
┌────────────▼────────────────────────────────────────────────┐
│                   Lovelace Backend                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  Wardrobe DB │  │ Photobooth   │  │ Video Call      │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  Calendar    │  │ Clothes Rec  │  │ Virtual Try-On  │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             Payment Agent (NEW!)                      │  │
│  │  - AI Shopping Assistant                              │  │
│  │  - UCP Protocol                                       │  │
│  │  - Stripe Integration                                 │  │
│  │  - Browser Automation                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Feature Integrations

### 1. Calendar-Aware Shopping

Payment Agent can check your calendar to recommend appropriate outfits:

```python
# Backend integration
from src.PaymentAgent import PaymentAgent
from src.GoogleCalendarSync.google_calendar import get_upcoming_events

agent = PaymentAgent()

# Get user's calendar
events = get_upcoming_events(user_id, days=7)

# Agent uses calendar context
response = await agent.chat(
    "I need something to wear",
    user_context={"calendar_events": events}
)
# Agent: "I see you have a wedding on Saturday! Let me find some elegant dresses..."
```

### 2. Wardrobe-Aware Recommendations

Avoid buying duplicates by checking existing wardrobe:

```python
from src.WardrobeDB.wardrobe_db import get_user_wardrobe

wardrobe = get_user_wardrobe(user_id)

response = await agent.chat(
    "Show me summer dresses",
    user_context={"wardrobe": wardrobe}
)
# Agent considers existing items to suggest complementary pieces
```

### 3. Virtual Try-On Before Purchase

Try items before buying:

```python
# User flow:
# 1. Search products with Payment Agent
# 2. Try on with VTO
# 3. Purchase if satisfied

# Search
products = await agent._search_products("blue dress")

# Try on (using VTO module)
from src.VirtualTryOn.virtual_tryon import try_on_garment
tryon_result = try_on_garment(user_image, products[0]["image"])

# Add to cart if satisfied
if user_likes_it:
    await agent._add_to_cart(products[0]["id"])
```

### 4. Photobooth with New Purchases

Take photos with the virtual boyfriend after purchase:

```python
# After successful purchase
order = await agent._complete_checkout(checkout_id, confirm=True)

# Celebrate with photobooth
from src.Photobooth.photobooth import create_photobooth_image
celebration = create_photobooth_image(
    user_image,
    boyfriend_model,
    background="shopping_celebration",
    text=f"New outfit! Order #{order['order_number']}"
)
```

### 5. Product 3D Pipeline Integration

Convert purchased items to 3D for AR try-on:

```python
from src.ProductTo3DPipeline.product_to_3d_pipeline import convert_product_to_3d

# After purchase, convert to 3D
product_image = order["items"][0]["image_url"]
model_3d = convert_product_to_3d(
    product_image,
    quality="standard"
)

# Store in wardrobe with 3D model
add_to_wardrobe(user_id, {
    "product_id": order["items"][0]["id"],
    "model_3d": model_3d,
    "purchase_date": order["created_at"]
})
```

## Frontend Integration

### Creating a Shopping Modal Component

```typescript
// frontend/components/shopping-modal.tsx

import { useState } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';

export function ShoppingModal({ isOpen, onClose }) {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  
  const sendMessage = async () => {
    const response = await fetch('/payment-agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        context: {
          // Pass calendar events
          calendar_events: await fetchCalendarEvents(),
          // Pass wardrobe
          wardrobe: await fetchWardrobe()
        }
      })
    });
    
    const data = await response.json();
    setChatHistory([...chatHistory, 
      { role: 'user', content: message },
      { role: 'assistant', content: data.response }
    ]);
    setMessage('');
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <div className="space-y-4">
          <h2>AI Shopping Assistant</h2>
          
          {/* Chat history */}
          <div className="space-y-2">
            {chatHistory.map((msg, i) => (
              <div key={i} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
                <p className="inline-block bg-gray-100 rounded px-4 py-2">
                  {msg.content}
                </p>
              </div>
            ))}
          </div>
          
          {/* Input */}
          <div className="flex gap-2">
            <input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="What are you looking for?"
              className="flex-1 border rounded px-4 py-2"
            />
            <button onClick={sendMessage} className="bg-blue-500 text-white px-4 py-2 rounded">
              Send
            </button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

### Adding to Main App

```typescript
// frontend/components/main-app.tsx

import { ShoppingModal } from './shopping-modal';

export function MainApp() {
  const [showShopping, setShowShopping] = useState(false);
  
  return (
    <div>
      {/* Existing features */}
      <button onClick={() => setShowVideoCall(true)}>
        Video Call
      </button>
      <button onClick={() => setShowPhotobooth(true)}>
        Photobooth
      </button>
      
      {/* NEW: Shopping button */}
      <button onClick={() => setShowShopping(true)}>
        🛍️ Shop with AI
      </button>
      
      <ShoppingModal 
        isOpen={showShopping}
        onClose={() => setShowShopping(false)}
      />
    </div>
  );
}
```

## API Endpoints

All endpoints are available at `/payment-agent/*`:

### Chat
```http
POST /payment-agent/chat
{
  "message": "I need a dress for a wedding",
  "context": {
    "calendar_events": [...],
    "wardrobe": [...]
  }
}
```

### Search Products
```http
POST /payment-agent/search-products
{
  "query": "summer dress",
  "limit": 10
}
```

### Cart Operations
```http
POST /payment-agent/cart/add
GET /payment-agent/cart
DELETE /payment-agent/cart/clear
```

### Checkout
```http
POST /payment-agent/checkout/create
POST /payment-agent/checkout/complete
```

### Order Status
```http
POST /payment-agent/order/status
{
  "order_id": "order_123"
}
```

## Configuration

Add to `backend/.env`:

```env
# Payment Agent
GEMINI_API_KEY=your_gemini_api_key
STRIPE_SECRET_KEY=sk_test_your_stripe_key
PAYMENT_AGENT_ENABLE_BROWSER=true
```

## Testing the Integration

1. **Start backend**:
```bash
cd backend
python main.py
```

2. **Check health**:
```bash
curl http://localhost:8000/health
# Should show payment_agent: "active"
```

3. **Test chat**:
```bash
curl -X POST http://localhost:8000/payment-agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me dresses"}'
```

## User Flow Examples

### Example 1: Event-Based Shopping

```
1. User opens app
2. Virtual boyfriend: "You have a wedding Saturday! Need something?"
3. User: "Yes, show me options"
4. Agent searches products
5. User tries on items virtually
6. User adds to cart
7. Agent creates checkout
8. User confirms purchase
9. Takes photobooth pic with boyfriend celebrating
```

### Example 2: Wardrobe Gap Analysis

```
1. Agent analyzes wardrobe
2. Agent: "You have lots of casual wear but few formal pieces"
3. User: "Find me professional work outfits"
4. Agent shows curated options
5. User selects items
6. Agent handles checkout
7. Items added to wardrobe DB with 3D models
```

## Security Considerations

1. **User Confirmation**: Always require explicit confirmation before purchases
2. **Amount Display**: Show clear totals before checkout
3. **Secure Storage**: Payment methods stored via Stripe, not locally
4. **Audit Logs**: Log all transactions for user review

## Next Steps

1. Create frontend shopping modal
2. Integrate with calendar sync
3. Add wardrobe awareness
4. Test with real Stripe account
5. Enable browser automation for specific merchants
6. Add order history view

## Support

- API Documentation: http://localhost:8000/docs
- Test setup: `python backend/src/PaymentAgent/test_setup.py`
- Run demo: `python backend/src/PaymentAgent/demo.py`

## Future Enhancements

- [ ] Multi-currency support
- [ ] Price drop alerts
- [ ] Subscription management
- [ ] Return/refund handling
- [ ] Multi-merchant cart
- [ ] Social shopping (share with friends)
- [ ] Voice shopping
- [ ] AR try-on integration

---

**The Payment Agent is ready to transform Lovelace into a complete agentic shopping experience!** 🛍️✨
