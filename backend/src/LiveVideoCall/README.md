# Lovelace - Live Video Call with Gemini Live API

This module implements real-time video call functionality using Google's Gemini Live API, enabling the Virtual Boyfriend avatar to see, hear, and respond to users naturally.

## ✨ Features

- 🎤 **Real-time audio conversations** with natural voice
- 📹 **Video input support** for outfit analysis
- 🧠 **AI-powered responses** with avatar personality
- 🔧 **Function calling** for wardrobe, calendar, and outfit tools
- 💬 **Text chat mode** for testing and development
- 🎭 **Customizable voices** and avatar personalities
- 📝 **Conversation history** tracking
- 🔄 **Session management** with reconnection support

## 🚀 Quick Start

### 1. Install Dependencies

Already done if you installed from root `requirements.txt`:

```bash
pip install google-genai python-dotenv
```

### 2. Get Gemini API Key

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy your key

### 3. Configure Environment

Create a `.env` file in the **project root** directory:

```bash
GOOGLE_API_KEY=your_api_key_here
```

### 4. Run Quick Test

```bash
cd backend/src/LiveVideoCall
python demo.py --quick
```

### 5. Try Interactive Mode

```bash
python demo.py --interactive
```

## 📖 Usage Examples

### Basic Text Conversation

```python
from LiveVideoCall.live_video_call import (
    LiveVideoCallManager,
    SessionConfig,
    ResponseModality
)

# Create manager
manager = LiveVideoCallManager()

# Create session
config = SessionConfig(
    user_id="user123",
    response_modality=ResponseModality.TEXT
)
session_id = await manager.create_session("user123", config)
session = await manager.get_session(session_id)

# Chat
async with session.session as sess:
    await sess.send(input="What should I wear today?", end_of_turn=True)

    async for response in sess.receive():
        if hasattr(response, 'text'):
            print(response.text)
        if response.server_content.turn_complete:
            break

# Close
await manager.close_session(session_id)
```

### With Custom Avatar Personality

```python
config = SessionConfig(
    user_id="user123",
    system_instruction="""You are a supportive, enthusiastic fashion expert
    who loves helping people feel confident. Be encouraging, specific, and fun!""",
    temperature=0.9,
    voice_name=VoiceName.KORE
)
```

### Register Custom Tools

```python
# Define tool
outfit_tool = {
    "function_declarations": [{
        "name": "save_outfit",
        "description": "Save an outfit combination",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {"type": "array", "items": {"type": "string"}},
                "name": {"type": "string"}
            }
        }
    }]
}

# Define handler
async def handle_save_outfit(**kwargs):
    # Your logic here
    return {"success": True, "outfit_id": "outfit_123"}

# Register
session.register_tool(outfit_tool, handle_save_outfit)
```

## 🎮 Demo Commands

Run different demos:

```bash
# All demos
python demo.py

# Quick API test
python demo.py --quick

# Interactive chat
python demo.py --interactive

# Scenario demos
python demo.py --scenarios

# Text conversation only
python demo.py --text

# Tool calling demo
python demo.py --tools

# Audio configuration
python demo.py --audio-config
```

## 🎨 Customization

### Available Voices

- `VoiceName.KORE` - Warm, friendly male voice (default)
- `VoiceName.CHARON` - Deep, resonant male voice
- `VoiceName.FENRIR` - Energetic male voice
- `VoiceName.AOEDE` - Female voice
- `VoiceName.PUCK` - Playful voice

### Response Modalities

- `ResponseModality.TEXT` - Text responses (easier for development)
- `ResponseModality.AUDIO` - Audio responses (requires audio playback)

### Configuration Options

```python
SessionConfig(
    user_id="user123",
    response_modality=ResponseModality.AUDIO,
    voice_name=VoiceName.KORE,
    enable_video=True,
    enable_audio=True,
    system_instruction="Custom personality...",
    temperature=0.8,  # 0.0-1.0, higher = more creative
    top_k=40,
    top_p=0.95,
    max_output_tokens=8192
)
```

## 🔧 Integration with Other Modules

### WardrobeDB Integration

```python
from WardrobeDB.wardrobe_db import WardrobeManager

wardrobe_manager = WardrobeManager()

async def handle_wardrobe_lookup(**kwargs):
    items = await wardrobe_manager.search_items(
        user_id=session.config.user_id,
        category=kwargs.get('category')
    )
    return {"items": [item.to_dict() for item in items]}
```

### Google Calendar Integration

```python
from GoogleCalendarSync.google_calendar import CalendarManager

calendar_manager = CalendarManager()

async def handle_check_calendar(**kwargs):
    events = await calendar_manager.get_upcoming_events(
        user_id=session.config.user_id,
        days_ahead=7
    )
    return {"events": events}
```

## ⚠️ Important Notes

### Session Duration Limits

- **Audio-only**: ~15 minutes
- **Audio + Video**: ~2 minutes
- Implement reconnection logic for longer conversations

### API Quotas

Free tier has rate limits. For production:

- Monitor token usage
- Implement exponential backoff
- Consider paid tier

### Security

- Never expose API keys in frontend
- Use server-to-server communication
- Store credentials securely

## 🐛 Troubleshooting

### "API key not found"

Make sure `.env` is in the **project root** (not in backend or src):

```
HnR-2026-Lovelace/
├── .env              ← Here!
├── backend/
│   └── src/
│       └── LiveVideoCall/
└── frontend/
```

### Import errors

Make sure you're running from the correct directory:

```bash
# From backend/src/LiveVideoCall:
python demo.py

# From project root:
python -m backend.src.LiveVideoCall.demo
```

### Connection fails

1. Check API key is valid at https://aistudio.google.com/
2. Verify internet connection
3. Check for rate limiting (wait a minute and retry)

## 📚 Resources

- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Live API Guide](https://ai.google.dev/gemini-api/docs/live)
- [Python SDK](https://github.com/google/generative-ai-python)

## 🎯 Next Steps

1. ✅ Set up API key
2. ✅ Run quick test
3. 🔲 Try interactive mode
4. 🔲 Test with scenarios
5. 🔲 Integrate with WardrobeDB
6. 🔲 Add to FastAPI backend
7. 🔲 Connect frontend UI
8. 🔲 Implement audio/video streaming

## 📝 API Reference

See `SETUP.txt` for detailed setup instructions and `live_video_call.py` for full API documentation.
