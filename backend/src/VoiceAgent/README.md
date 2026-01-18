# Voice Agent - Gemini Live API Integration

## Overview

The Voice Agent provides voice-controlled navigation and conversation using Google's Gemini Live API. Users can talk naturally to their virtual boyfriend to control the app.

## Features

### 🎤 Voice Control
- **Natural Language**: Talk naturally, no specific commands needed
- **Feature Navigation**: Open any feature by voice ("open the calendar", "show my wardrobe")
- **Conversational AI**: Get fashion advice and chat naturally
- **Real-time Processing**: Instant response to voice commands

### 🚀 Supported Commands

The agent can open these features via voice:

| Voice Command Examples | Opens Feature |
|------------------------|---------------|
| "Open video call", "Start a video call" | Video Call |
| "Try on clothes", "Virtual try-on" | Virtual Try-On |
| "Take a photo", "Open photobooth" | Photobooth |
| "Shop for dresses", "Find clothes" | Search Products |
| "Show recommendations", "Style advice" | Outfit Recommendations |
| "Open calendar", "Show my events" | Calendar |
| "Show my wardrobe", "Open profile" | Wardrobe/Profile |

### 💬 Conversational Features

- Ask for fashion advice
- Discuss outfit choices
- Get styling tips
- Plan outfits for events
- General conversation about fashion

## Architecture

```
┌─────────────────┐
│  Frontend UI    │
│  (Main App)     │
└────────┬────────┘
         │ WebSocket
         │
┌────────▼────────────────────────┐
│  Backend Voice Agent            │
│  /voice-agent/ws                │
├─────────────────────────────────┤
│  • Audio streaming              │
│  • Gemini Live API              │
│  • Function calling (tools)     │
│  • TTS audio response           │
└────────┬────────────────────────┘
         │
┌────────▼────────┐
│  Gemini Live    │
│  API            │
└─────────────────┘
```

## Implementation

### Backend (`backend/src/VoiceAgent/`)

**`voice_agent.py`** - Main voice agent with:
- WebSocket endpoint `/voice-agent/ws`
- Gemini Live API integration
- Function calling for navigation
- Audio processing (input/output)

**Tools Defined:**
- `open_video_call`
- `open_virtual_tryon`
- `open_photobooth`
- `open_shop`
- `open_recommendations`
- `open_calendar`
- `open_wardrobe`

### Frontend (`frontend/components/main-app.tsx`)

**Features:**
- WebSocket connection to voice agent
- Real-time audio streaming
- Function call handling
- UI updates based on voice commands

**States:**
- `isConnected` - WebSocket connection status
- `isRecording` - Microphone recording state
- `chatMessages` - Conversation history

## Usage

### For Users

1. **Click the microphone button** in the chat input
2. **Speak naturally**: "Open the calendar"
3. **Watch it work**: The feature opens automatically
4. **Continue talking**: Ask follow-up questions

### Voice Input Flow

```
User clicks mic → Start recording → Stream audio → 
Gemini processes → Function call detected → 
Feature opens → Response spoken back
```

### Text Input Alternative

Users can also type commands:
- "open calendar"
- "show my wardrobe"
- "take a photo with you"

## Configuration

### Environment Variables

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
GEMINI_MODEL=gemini-2.0-flash-exp
```

### System Instruction

The agent has a specific personality:
```python
system_instruction = """You are a helpful and friendly virtual boyfriend 
assistant for Lovelace, a fashion app. You help users with their wardrobe, 
style, and shopping needs. Be conversational, friendly, and helpful."""
```

## API Reference

### WebSocket Endpoint

**URL**: `ws://localhost:8000/voice-agent/ws`

**Messages to Backend:**

```json
// Text message
{
  "type": "text",
  "content": "open the calendar"
}

// Audio chunk
{
  "type": "audio",
  "data": "base64_encoded_audio"
}

// Recording control
{
  "type": "start_recording"
}
{
  "type": "stop_recording"
}
```

**Messages from Backend:**

```json
// Text response
{
  "type": "text",
  "content": "Opening your calendar..."
}

// Function call (feature navigation)
{
  "type": "function_call",
  "function": "open_calendar",
  "args": {}
}

// Audio response (TTS)
{
  "type": "audio",
  "content": "base64_encoded_audio"
}

// Status update
{
  "type": "status",
  "content": "Processing..."
}
```

## Testing

### 1. Test WebSocket Connection

```bash
# Start backend
cd backend
python main.py

# Check voice agent is loaded
curl http://localhost:8000/health
# Should show: "voice_agent": "active"
```

### 2. Test Voice Commands

1. Open the app
2. Click microphone button
3. Say: "Open the calendar"
4. Verify calendar modal opens

### 3. Test Text Commands

1. Type: "open photobooth"
2. Press enter
3. Verify photobooth opens

## Troubleshooting

### WebSocket Not Connecting

- Check backend is running
- Verify GEMINI_API_KEY is set
- Check browser console for errors

### Microphone Not Working

- Check browser permissions
- Ensure HTTPS (or localhost)
- Try refreshing the page

### Commands Not Working

- Check Gemini API quota
- Verify function tools are defined
- Check backend logs

### No Audio Response

- TTS integration may need setup
- Check audio context permissions
- Verify audio decoding

## Future Enhancements

- [ ] Add voice activity detection
- [ ] Implement TTS for responses
- [ ] Add wake word ("Hey boyfriend")
- [ ] Multi-language support
- [ ] Voice biometrics for personalization
- [ ] Emotion detection in voice
- [ ] Background conversation mode

## Security

- Audio is streamed securely via WebSocket
- No audio stored on backend
- User permission required for microphone
- API key never exposed to frontend

---

**The voice agent makes Lovelace truly hands-free!** 🎤✨
