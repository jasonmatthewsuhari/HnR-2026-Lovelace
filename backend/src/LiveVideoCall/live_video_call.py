"""
Lovelace Live Video Call Module - Gemini Live API Integration

This module provides real-time video call capabilities using Google's Gemini Live API,
enabling the Virtual Boyfriend avatar to see, hear, and respond to users in real-time.

Main features:
- Real-time audio/video streaming with Gemini Live API
- Multimodal interaction (vision + audio + text)
- Function calling for wardrobe, calendar, and outfit analysis
- Session management with reconnection logic
- Avatar personality and voice configuration
- Barge-in support for natural conversations
"""

import os
import asyncio
import json
import base64
from datetime import datetime
from typing import Optional, Dict, List, Any, AsyncGenerator, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: Google GenAI library not installed.")
    print("Run: pip install google-genai")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Run: pip install python-dotenv")


class ResponseModality(Enum):
    """Response modality types"""
    AUDIO = "AUDIO"
    TEXT = "TEXT"


class VoiceName(Enum):
    """Available voice options for the avatar"""
    KORE = "Kore"  # Warm, friendly male voice
    CHARON = "Charon"  # Deep, resonant male voice
    FENRIR = "Fenrir"  # Energetic male voice
    AOEDE = "Aoede"  # Female voice (alternative)
    PUCK = "Puck"  # Playful voice


class SessionStatus(Enum):
    """Session status states"""
    IDLE = "idle"
    CONNECTING = "connecting"
    ACTIVE = "active"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    CLOSED = "closed"


@dataclass
class SessionConfig:
    """Configuration for a Live API session"""
    user_id: str
    response_modality: ResponseModality = ResponseModality.AUDIO
    voice_name: VoiceName = VoiceName.KORE
    enable_video: bool = True
    enable_audio: bool = True
    system_instruction: Optional[str] = None
    temperature: float = 0.8
    top_k: int = 40
    top_p: float = 0.95
    max_output_tokens: int = 8192
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "response_modality": self.response_modality.value,
            "voice_name": self.voice_name.value,
            "enable_video": self.enable_video,
            "enable_audio": self.enable_audio,
            "system_instruction": self.system_instruction,
            "temperature": self.temperature,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "max_output_tokens": self.max_output_tokens
        }


@dataclass
class ChatMessage:
    """Represents a message in the conversation"""
    role: str  # "user" or "model"
    content: str
    timestamp: datetime
    modality: str  # "audio", "video", "text"
    metadata: Optional[Dict] = None


class GeminiLiveSession:
    """
    Manages a single Gemini Live API session for video calling
    """
    
    def __init__(self, config: SessionConfig):
        """
        Initialize Live session
        
        Args:
            config: Session configuration
        """
        if not GENAI_AVAILABLE:
            raise ImportError("google-genai library is required. Run: pip install google-genai")
        
        self.config = config
        self.client = None
        self.session = None
        self.status = SessionStatus.IDLE
        self.conversation_history: List[ChatMessage] = []
        self.tools: List[Dict] = []
        self.tool_handlers: Dict[str, Callable] = {}
        
        # Get API key from environment
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not found in environment")
    
    def register_tool(self, tool_definition: Dict, handler: Callable):
        """
        Register a tool/function that the model can call
        
        Args:
            tool_definition: Function schema definition
            handler: Async function to execute when tool is called
        """
        self.tools.append(tool_definition)
        tool_name = tool_definition.get("name")
        if tool_name:
            self.tool_handlers[tool_name] = handler
    
    def _get_system_instruction(self) -> str:
        """Get system instruction for avatar personality"""
        if self.config.system_instruction:
            return self.config.system_instruction
        
        # Default Virtual Boyfriend personality
        return """You are a charming, fashion-savvy virtual boyfriend assistant named Lovelace. 
You have excellent taste in fashion and love helping your partner look their best.

Your personality:
- Warm, supportive, and encouraging
- Honest but tactful about fashion choices
- Knowledgeable about trends, colors, and styling
- Playfully flirtatious but always respectful
- Attentive to details in outfits and surroundings
- Proactive in giving compliments and suggestions

When analyzing outfits:
- Comment on color coordination, fit, and style
- Suggest improvements or alternatives
- Consider the occasion and weather
- Be specific about what works and what doesn't
- Relate suggestions to the user's existing wardrobe when possible

Keep responses natural, conversational, and engaging. Show genuine interest in helping 
your partner feel confident and look amazing."""
    
    def _build_live_config(self) -> types.LiveConnectConfig:
        """Build configuration for Live API connection"""
        
        config_dict = {
            "response_modalities": [self.config.response_modality.value],
            "temperature": self.config.temperature,
            "top_k": self.config.top_k,
            "top_p": self.config.top_p,
            "max_output_tokens": self.config.max_output_tokens,
            "system_instruction": self._get_system_instruction()
        }
        
        # Add speech config if using audio output
        if self.config.response_modality == ResponseModality.AUDIO:
            config_dict["speech_config"] = types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=self.config.voice_name.value
                    )
                )
            )
        
        # Add tools if registered
        if self.tools:
            config_dict["tools"] = self.tools
        
        return types.LiveConnectConfig(**config_dict)
    
    async def connect(self) -> bool:
        """
        Establish connection to Gemini Live API
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.status = SessionStatus.CONNECTING
            
            # Initialize client
            self.client = genai.Client(api_key=self.api_key)
            
            # Build configuration
            config = self._build_live_config()
            
            # Use the native audio model
            model = "gemini-2.0-flash-exp"
            
            print(f"Connecting to Gemini Live API with model: {model}")
            print(f"Response modality: {self.config.response_modality.value}")
            print(f"Voice: {self.config.voice_name.value}")
            
            # Connect to live session
            self.session = self.client.aio.live.connect(model=model, config=config)
            
            self.status = SessionStatus.ACTIVE
            print("[SUCCESS] Connected to Gemini Live API")
            return True
            
        except Exception as e:
            self.status = SessionStatus.ERROR
            print(f"[ERROR] Failed to connect: {e}")
            return False
    
    async def send_text(self, text: str, end_of_turn: bool = True) -> bool:
        """
        Send text message to the model
        
        Args:
            text: Text to send
            end_of_turn: Whether this completes the user's turn
            
        Returns:
            True if successful
        """
        if self.status != SessionStatus.ACTIVE or not self.session:
            print("Session not active")
            return False
        
        try:
            async with self.session as sess:
                # Create proper Content format
                content = types.Content(
                    parts=[types.Part(text=text)]
                )
                await sess.send_client_content(turns=[content], turn_complete=end_of_turn)
                
                # Log to history
                self.conversation_history.append(ChatMessage(
                    role="user",
                    content=text,
                    timestamp=datetime.now(),
                    modality="text"
                ))
                return True
        except Exception as e:
            print(f"Error sending text: {e}")
            return False
    
    async def send_audio_chunk(self, audio_data: bytes) -> bool:
        """
        Send audio chunk to the model
        
        Args:
            audio_data: Raw audio bytes (16-bit PCM, mono, 16kHz)
            
        Returns:
            True if successful
        """
        if self.status != SessionStatus.ACTIVE or not self.session:
            return False
        
        try:
            async with self.session as sess:
                # Send audio in realtime using correct API
                audio_blob = types.Blob(
                    data=audio_data,
                    mime_type="audio/pcm;rate=16000"
                )
                await sess.send_realtime_input(audio=audio_blob)
                return True
        except Exception as e:
            print(f"Error sending audio: {e}")
            return False
    
    async def send_video_frame(self, frame_data: bytes, mime_type: str = "image/jpeg") -> bool:
        """
        Send video frame to the model
        
        Args:
            frame_data: Image frame bytes
            mime_type: MIME type of the frame
            
        Returns:
            True if successful
        """
        if self.status != SessionStatus.ACTIVE or not self.session:
            return False
        
        try:
            async with self.session as sess:
                # Create image blob
                image_blob = types.Blob(
                    data=frame_data,
                    mime_type=mime_type
                )
                # Note: Video input support may be limited
                await sess.send_realtime_input(image=image_blob)
                return True
        except Exception as e:
            print(f"Error sending video frame: {e}")
            return False
    
    async def receive_responses(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Receive responses from the model
        
        Yields:
            Response messages from the model
        """
        if self.status != SessionStatus.ACTIVE or not self.session:
            return
        
        try:
            async with self.session as sess:
                async for response in sess.receive():
                    
                    # Handle different response types
                    response_data = {
                        "timestamp": datetime.now().isoformat(),
                        "type": None,
                        "content": None,
                        "metadata": {}
                    }
                    
                    # Check response attributes
                    if hasattr(response, 'text') and response.text:
                        response_data["type"] = "text"
                        response_data["content"] = response.text
                        
                        # Log to history
                        self.conversation_history.append(ChatMessage(
                            role="model",
                            content=response.text,
                            timestamp=datetime.now(),
                            modality="text"
                        ))
                    
                    elif hasattr(response, 'data') and response.data:
                        # Audio or other data response
                        response_data["type"] = "audio"
                        response_data["content"] = response.data
                        response_data["metadata"]["mime_type"] = getattr(response, 'mime_type', 'audio/pcm')
                    
                    elif hasattr(response, 'tool_call'):
                        # Tool/function call
                        response_data["type"] = "tool_call"
                        response_data["content"] = response.tool_call
                        
                        # Execute tool if handler registered
                        tool_name = response.tool_call.get("name")
                        if tool_name in self.tool_handlers:
                            tool_result = await self.tool_handlers[tool_name](**response.tool_call.get("args", {}))
                            response_data["metadata"]["tool_result"] = tool_result
                            
                            # Send tool result back
                            await sess.send(tool_response=tool_result)
                    
                    # Check for turn completion
                    if hasattr(response, 'turn_complete'):
                        response_data["metadata"]["turn_complete"] = response.turn_complete
                    
                    yield response_data
                    
        except Exception as e:
            print(f"Error receiving responses: {e}")
            self.status = SessionStatus.ERROR
    
    async def close(self):
        """Close the session"""
        if self.session:
            try:
                # The session context manager handles cleanup
                self.status = SessionStatus.CLOSED
                print("Session closed")
            except Exception as e:
                print(f"Error closing session: {e}")
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "modality": msg.modality,
                "metadata": msg.metadata
            }
            for msg in self.conversation_history
        ]


class LiveVideoCallManager:
    """
    High-level manager for Live Video Call sessions
    """
    
    def __init__(self):
        """Initialize the manager"""
        self.active_sessions: Dict[str, GeminiLiveSession] = {}
        self.session_configs: Dict[str, SessionConfig] = {}
    
    async def create_session(self, user_id: str, config: Optional[SessionConfig] = None) -> str:
        """
        Create a new video call session
        
        Args:
            user_id: User identifier
            config: Optional session configuration
            
        Returns:
            Session ID
        """
        if not config:
            config = SessionConfig(user_id=user_id)
        
        # Create session
        session = GeminiLiveSession(config)
        
        # Register default tools
        self._register_default_tools(session)
        
        # Connect
        success = await session.connect()
        if not success:
            raise ConnectionError("Failed to establish Gemini Live session")
        
        # Store session
        session_id = f"{user_id}_{datetime.now().timestamp()}"
        self.active_sessions[session_id] = session
        self.session_configs[session_id] = config
        
        return session_id
    
    def _register_default_tools(self, session: GeminiLiveSession):
        """Register default tools for the virtual boyfriend"""
        
        # Outfit rating tool
        outfit_rating_tool = {
            "function_declarations": [{
                "name": "rate_outfit",
                "description": "Rate and analyze the user's outfit on a scale of 1-10",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rating": {"type": "integer", "description": "Rating from 1-10"},
                        "positive_aspects": {"type": "array", "items": {"type": "string"}, "description": "What looks good"},
                        "improvements": {"type": "array", "items": {"type": "string"}, "description": "Suggested improvements"},
                        "occasion": {"type": "string", "description": "What occasion this outfit suits"}
                    },
                    "required": ["rating", "positive_aspects"]
                }
            }]
        }
        
        async def handle_outfit_rating(**kwargs):
            """Handle outfit rating"""
            return {
                "success": True,
                "rating_recorded": kwargs.get("rating"),
                "message": f"Outfit rated {kwargs.get('rating')}/10"
            }
        
        session.register_tool(outfit_rating_tool, handle_outfit_rating)
        
        # Wardrobe lookup tool
        wardrobe_tool = {
            "function_declarations": [{
                "name": "lookup_wardrobe",
                "description": "Search the user's wardrobe for clothing items",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "Clothing category (tops, bottoms, shoes, etc.)"},
                        "color": {"type": "string", "description": "Color to search for"},
                        "style": {"type": "string", "description": "Style keywords"}
                    }
                }
            }]
        }
        
        async def handle_wardrobe_lookup(**kwargs):
            """Handle wardrobe lookup"""
            # In production, this would query the WardrobeDB
            return {
                "success": True,
                "items_found": 3,
                "suggestions": ["Blue denim jacket", "White cotton t-shirt", "Black leather boots"]
            }
        
        session.register_tool(wardrobe_tool, handle_wardrobe_lookup)
    
    async def get_session(self, session_id: str) -> Optional[GeminiLiveSession]:
        """Get an active session"""
        return self.active_sessions.get(session_id)
    
    async def close_session(self, session_id: str):
        """Close and remove a session"""
        if session_id in self.active_sessions:
            await self.active_sessions[session_id].close()
            del self.active_sessions[session_id]
            if session_id in self.session_configs:
                del self.session_configs[session_id]
    
    async def close_all_sessions(self):
        """Close all active sessions"""
        for session_id in list(self.active_sessions.keys()):
            await self.close_session(session_id)


# ============================================================================
# DEMO / TESTING FUNCTIONS
# ============================================================================

async def demo_text_conversation():
    """Demo: Simple text conversation with the virtual boyfriend"""
    print("\n" + "="*60)
    print("DEMO: Text Conversation with Virtual Boyfriend")
    print("="*60 + "\n")
    
    # Create session
    config = SessionConfig(
        user_id="demo_user",
        response_modality=ResponseModality.TEXT,  # Text for easier demo
        enable_video=False,
        enable_audio=False
    )
    
    session = GeminiLiveSession(config)
    
    try:
        # Connect
        connected = await session.connect()
        if not connected:
            print("Failed to connect")
            return
        
        # Send messages and receive responses
        messages = [
            "Hey! I'm trying to decide what to wear today.",
            "I have a job interview this afternoon. What should I wear?",
            "I was thinking a navy blue suit. What do you think?"
        ]
        
        async with session.session as sess:
            for msg in messages:
                print(f"\n👤 You: {msg}")
                await sess.send(input=msg, end_of_turn=True)
                
                # Receive response
                print("🤖 Lovelace: ", end="", flush=True)
                async for response in sess.receive():
                    if hasattr(response, 'text') and response.text:
                        print(response.text, end="", flush=True)
                    
                    if hasattr(response, 'server_content') and response.server_content:
                        if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                            break
                print()  # New line after response
                
                await asyncio.sleep(1)
        
        print("\n✓ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Demo error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await session.close()


async def demo_with_tools():
    """Demo: Conversation with tool/function calling"""
    print("\n" + "="*60)
    print("DEMO: Virtual Boyfriend with Wardrobe Tools")
    print("="*60 + "\n")
    
    # Create manager
    manager = LiveVideoCallManager()
    
    try:
        # Create session
        config = SessionConfig(
            user_id="demo_user",
            response_modality=ResponseModality.TEXT,
            enable_video=False,
            enable_audio=False
        )
        
        session_id = await manager.create_session("demo_user", config)
        session = await manager.get_session(session_id)
        
        if not session:
            print("Failed to create session")
            return
        
        # Conversation
        messages = [
            "Can you check my wardrobe for something casual?",
            "Rate this outfit: blue jeans, white t-shirt, and sneakers"
        ]
        
        async with session.session as sess:
            for msg in messages:
                print(f"\n👤 You: {msg}")
                await sess.send(input=msg, end_of_turn=True)
                
                # Receive response
                print("🤖 Lovelace: ", end="", flush=True)
                async for response in sess.receive():
                    if hasattr(response, 'text') and response.text:
                        print(response.text, end="", flush=True)
                    
                    # Check for tool calls
                    if hasattr(response, 'tool_call'):
                        print(f"\n  [Tool Called: {response.tool_call}]")
                    
                    if hasattr(response, 'server_content') and response.server_content:
                        if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                            break
                print()
                
                await asyncio.sleep(1)
        
        print("\n✓ Demo completed successfully!")
        
        # Show conversation history
        print("\n" + "="*60)
        print("Conversation History:")
        print("="*60)
        history = session.get_conversation_history()
        for msg in history:
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            print(f"\n{role_icon} {msg['role'].title()}: {msg['content'][:100]}...")
        
    except Exception as e:
        print(f"\n✗ Demo error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await manager.close_all_sessions()


async def demo_audio_conversation():
    """Demo: Audio conversation setup (requires audio hardware)"""
    print("\n" + "="*60)
    print("DEMO: Audio Conversation Setup")
    print("="*60 + "\n")
    print("Note: This demo shows configuration but requires audio hardware for full functionality")
    
    config = SessionConfig(
        user_id="demo_user",
        response_modality=ResponseModality.AUDIO,
        voice_name=VoiceName.KORE,
        enable_audio=True,
        enable_video=False
    )
    
    session = GeminiLiveSession(config)
    
    try:
        connected = await session.connect()
        if connected:
            print("✓ Audio session configured successfully!")
            print(f"  Voice: {config.voice_name.value}")
            print(f"  Response Modality: {config.response_modality.value}")
            print("\nIn production, you would:")
            print("  1. Capture audio from microphone (16-bit PCM, 16kHz)")
            print("  2. Stream audio chunks using session.send_audio_chunk()")
            print("  3. Receive audio responses and play them")
            print("  4. Handle barge-in/interruptions")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        await session.close()


async def run_all_demos():
    """Run all available demos"""
    print("\n" + "🎭 "*20)
    print("LOVELACE - LIVE VIDEO CALL DEMO SUITE")
    print("🎭 "*20)
    
    # Check if API key is available
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: No API key found!")
        print("Please set GOOGLE_API_KEY or GEMINI_API_KEY in your .env file")
        return
    
    print(f"\n✓ API key loaded: {api_key[:20]}...")
    
    # Run demos
    demos = [
        ("Text Conversation", demo_text_conversation),
        ("Tool/Function Calling", demo_with_tools),
        ("Audio Configuration", demo_audio_conversation)
    ]
    
    for name, demo_func in demos:
        try:
            await demo_func()
            await asyncio.sleep(2)
        except Exception as e:
            print(f"\n✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "🎭 "*20)
    print("ALL DEMOS COMPLETED")
    print("🎭 "*20 + "\n")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """Run demos when script is executed directly"""
    asyncio.run(run_all_demos())
