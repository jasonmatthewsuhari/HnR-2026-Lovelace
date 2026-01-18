# Payment Agent - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
cd backend/src/PaymentAgent
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure API Keys

Edit `backend/.env` and add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
STRIPE_SECRET_KEY=sk_test_your_stripe_key_here
```

**Get your API keys:**
- Gemini: https://makersuite.google.com/app/apikey
- Stripe: https://dashboard.stripe.com/test/apikeys

### 3. Test Installation

```bash
python demo.py
```

## 📝 Basic Usage

### Python API

```python
from backend.src.PaymentAgent import PaymentAgent

# Initialize
agent = PaymentAgent()

# Chat with agent
response = await agent.chat("Show me summer dresses under $100")
print(response)
```

### REST API

```bash
# Start server
cd backend
python main.py

# Test endpoint
curl -X POST http://localhost:8000/payment-agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me summer dresses"}'
```

## 🎯 Key Features

1. **AI Shopping Assistant**: Natural language shopping
2. **UCP Protocol**: Standardized checkout with compatible merchants
3. **Secure Payments**: Shared Payment Tokens (SPT)
4. **Browser Fallback**: Auto-fills checkout forms for non-UCP merchants

## 📚 Next Steps

- Read full documentation: `README.md`
- Explore demo: `python demo.py`
- Check API routes: `routes.py`
- Review examples in code comments

## 🔧 Troubleshooting

**"GEMINI_API_KEY is required"**
→ Add your Gemini API key to `.env`

**"stripe.error.AuthenticationError"**
→ Check your Stripe API key is correct

**"playwright not found"**
→ Run: `playwright install chromium`

**Port 8000 already in use**
→ Change port in `backend/main.py` or kill existing process

## 💡 Tips

- Use test mode Stripe keys for development
- Browser automation works best with simple checkout flows
- UCP support is limited - most merchants need fallback
- Always test with small amounts first

## 🆘 Need Help?

- Check the main README.md
- Review demo.py for examples
- Check Stripe/Gemini API status
- Ensure all dependencies are installed

---

**Ready to build agentic commerce experiences!** 🛍️✨
