# Payment Agent - Demo Guide

## Available Demos

### 1. Auto-Play Demo (Recommended)
**File**: `demo_autoplay.py`  
**Description**: Self-running demo with no interaction required - perfect for showcasing!

```bash
python backend/src/PaymentAgent/demo_autoplay.py
```

**Features shown**:
- AI-powered conversation
- Product search
- Cart management
- UCP protocol
- Secure checkout
- Lovelace integration
- Complete shopping journey

**Duration**: ~2 minutes

---

### 2. Interactive Demo
**File**: `demo.py`  
**Description**: Full interactive demo where you control the pace

```bash
python backend/src/PaymentAgent/demo.py
```

**Features shown**:
- All features from auto-play demo
- Plus: API examples and detailed explanations
- Interactive: Press Enter to advance through sections

**Duration**: ~10 minutes (at your pace)

---

### 3. Setup Test
**File**: `test_setup.py`  
**Description**: Verify your installation is correct

```bash
python backend/src/PaymentAgent/test_setup.py
```

**Checks**:
- Environment variables
- Dependencies installed
- Module imports
- API connectivity (optional)

---

## Quick Start

### For Windows:

```cmd
cd backend\src\PaymentAgent
python demo_autoplay.py
```

### For Mac/Linux:

```bash
cd backend/src/PaymentAgent
python3 demo_autoplay.py
```

---

## What Each Demo Shows

| Feature | Auto-Play | Interactive | Test |
|---------|-----------|-------------|------|
| AI Conversation | ✓ | ✓ | - |
| Product Search | ✓ | ✓ | - |
| Cart Management | ✓ | ✓ | - |
| UCP Discovery | ✓ | ✓ | - |
| Secure Checkout | ✓ | ✓ | - |
| Browser Fallback | - | ✓ | - |
| Lovelace Integration | ✓ | ✓ | - |
| API Examples | - | ✓ | - |
| Setup Verification | - | - | ✓ |

---

## Demo Output Preview

### Auto-Play Demo

```
===================================================================
                                                                   
         PAYMENT AGENT - AUTO-PLAY DEMO                         
                                                                   
      Agentic Commerce with Universal Checkout Protocol        
                                                                   
===================================================================

A complete AI-powered shopping system for Lovelace

===================================================================
                    PART 1: INTRODUCTION                         
===================================================================

What is the Payment Agent?

The Payment Agent is an AI shopping assistant that combines:
  - Gemini AI for natural language understanding
  - Universal Checkout Protocol (UCP) for standardized checkout
  - Stripe for secure payments
  - Playwright for browser automation fallback

[... continues through 8 parts ...]
```

---

## Troubleshooting

### Demo doesn't start
- Make sure you're in the right directory
- Check Python is installed: `python --version`
- Try with full path: `python C:\path\to\demo_autoplay.py`

### Colors not showing
- Windows: Some terminals don't support ANSI colors
- Try Windows Terminal or PowerShell 7+
- Or run on Mac/Linux

### Import errors
- Run setup test first: `python test_setup.py`
- Install dependencies: `pip install -r requirements.txt`

---

## After Watching the Demo

### Next Steps:

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure API Keys**
   Add to `backend/.env`:
   ```env
   GEMINI_API_KEY=your_key_here
   STRIPE_SECRET_KEY=sk_test_your_key_here
   ```

3. **Test Setup**
   ```bash
   python test_setup.py
   ```

4. **Start Server**
   ```bash
   cd ../..
   python main.py
   ```

5. **Explore API**
   Visit: http://localhost:8000/docs

---

## Documentation

- **README.md** - Complete feature documentation
- **QUICKSTART.md** - 5-minute setup guide
- **INTEGRATION.md** - Integration with Lovelace
- **SUMMARY.md** - Implementation overview

---

## Need Help?

1. Run setup test: `python test_setup.py`
2. Check README.md for detailed docs
3. See QUICKSTART.md for setup help
4. Review code comments in demo files

---

**Enjoy the demo!** 🚀✨
