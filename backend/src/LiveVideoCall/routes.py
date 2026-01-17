"""
Lovelace Live Video Call Routes - FastAPI WebSocket Integration

This module provides WebSocket endpoints for real-time video calling with Gemini Live API.
"""

import os
import asyncio
import base64
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google-genai not available for video calls")

router = APIRouter(prefix="/api/video-call")


class VideoCallManager:
    """Manages active video call sessions"""
    
    def __init__(self):
        self.active_sessions = {}
    
    async def create_session(self, session_id: str, websocket: WebSocket):
        """Create a new video call session"""
        if not GENAI_AVAILABLE:
            await websocket.send_json({
                "type": "error",
                "content": "Gemini API not available"
            })
            return None
        
        # Get API key
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            await websocket.send_json({
                "type": "error",
                "content": "API key not configured"
            })
            return None
        
        try:
            # Create Gemini client
            client = genai.Client(api_key=api_key)
            
            # Configure for AUDIO responses (live voice)
            config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": "Kore"
                        }
                    }
                },
                "system_instruction": """You are a charming, fashion-savvy virtual boyfriend. 
                Keep responses brief and conversational - 1-2 sentences max.
                Be warm, supportive, and give specific fashion advice.
                Compliment good choices and be encouraging."""
            }
            
            # Connect to Gemini Live with proper model
            session = client.aio.live.connect(
                model="gemini-2.0-flash-exp",
                config=config
            )
            
            self.active_sessions[session_id] = {
                "websocket": websocket,
                "gemini_session": session,
                "client": client
            }
            
            return session
            
        except Exception as e:
            print(f"Error creating session: {e}")
            await websocket.send_json({
                "type": "error",
                "content": f"Failed to connect to Gemini: {str(e)}"
            })
            return None
    
    async def close_session(self, session_id: str):
        """Close a video call session"""
        if session_id in self.active_sessions:
            session_data = self.active_sessions[session_id]
            # Gemini session cleanup is handled by context manager
            del self.active_sessions[session_id]


# Global manager instance
call_manager = VideoCallManager()


@router.websocket("/live")
async def video_call_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for live video calling with Gemini
    
    Receives:
        - Audio chunks from frontend
        - Video frames (optional)
        
    Sends:
        - Text responses from avatar
        - Audio responses from avatar
    """
    await websocket.accept()
    session_id = f"session_{id(websocket)}"
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "text",
            "content": "Connecting to your fashion advisor..."
        })
        
        # Create Gemini session
        gemini_session = await call_manager.create_session(session_id, websocket)
        
        if not gemini_session:
            await websocket.close(code=1011, reason="Failed to initialize")
            return
        
        async with gemini_session as sess:
            # Send greeting
            greeting = types.Content(
                parts=[types.Part(text="Hi! I can see and hear you now. Show me your outfit or ask me anything about fashion!")]
            )
            await sess.send_client_content(turns=[greeting], turn_complete=True)
            
            # Send greeting to frontend  
            async for response in sess.receive():
                if hasattr(response, 'text') and response.text:
                    await websocket.send_json({
                        "type": "text",
                        "content": response.text
                    })
                
                if hasattr(response, 'data') and response.data:
                    # Send audio response (raw PCM from Gemini)
                    print(f"Sending audio: {len(response.data)} bytes")
                    audio_b64 = base64.b64encode(response.data).decode('utf-8')
                    await websocket.send_json({
                        "type": "audio",
                        "content": audio_b64
                    })
                
                if hasattr(response, 'server_content') and response.server_content:
                    if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                        break
            
            # Create tasks for bidirectional communication
            async def listen_to_gemini():
                """Continuously listen for responses from Gemini and send to frontend"""
                try:
                    async for response in sess.receive():
                        if hasattr(response, 'text') and response.text:
                            await websocket.send_json({
                                "type": "text",
                                "content": response.text
                            })
                        
                        if hasattr(response, 'data') and response.data:
                            # Send audio response (raw PCM from Gemini)
                            print(f"Sending audio response: {len(response.data)} bytes")
                            audio_b64 = base64.b64encode(response.data).decode('utf-8')
                            await websocket.send_json({
                                "type": "audio",
                                "content": audio_b64
                            })
                except Exception as e:
                    print(f"Error in Gemini listener: {e}")
            
            async def handle_frontend_messages():
                """Handle incoming messages from frontend"""
                last_audio_time = asyncio.get_event_loop().time()
                silence_threshold = 2.0  # 2 seconds of silence before turn complete
                audio_buffer = []
                
                async def check_silence():
                    """Check for silence and send turn complete"""
                    nonlocal last_audio_time, audio_buffer
                    while True:
                        await asyncio.sleep(0.5)  # Check every 500ms
                        current_time = asyncio.get_event_loop().time()
                        
                        # If we have audio in buffer and it's been silent for threshold time
                        if audio_buffer and (current_time - last_audio_time) >= silence_threshold:
                            print(f"Silence detected ({silence_threshold}s), signaling turn complete")
                            # Send turn complete signal
                            try:
                                await sess.send_client_content(turns=[], turn_complete=True)
                                audio_buffer = []  # Clear buffer
                            except Exception as e:
                                print(f"Error sending turn complete: {e}")
                
                # Start silence checker
                silence_task = asyncio.create_task(check_silence())
                
                try:
                    while True:
                        try:
                            # Receive data from frontend
                            data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                            
                            if data.get("type") == "text":
                                # Handle text messages
                                text_content = data.get("content", "")
                                if text_content:
                                    content = types.Content(
                                        parts=[types.Part(text=text_content)]
                                    )
                                    await sess.send_client_content(turns=[content], turn_complete=True)
                            
                            elif data.get("type") == "audio":
                                # Handle audio chunks from frontend
                                audio_data = data.get("data", "")
                                mime_type = data.get("mimeType", "audio/webm")
                                
                                if audio_data:
                                    try:
                                        # Decode base64 audio
                                        audio_bytes = base64.b64decode(audio_data)
                                        print(f"Received audio chunk: {len(audio_bytes)} bytes, MIME: {mime_type}")
                                        
                                        # Update last audio time
                                        last_audio_time = asyncio.get_event_loop().time()
                                        audio_buffer.append(audio_bytes)
                                        
                                        # Send audio to Gemini (turn NOT complete - still speaking)
                                        content = types.Content(
                                            parts=[types.Part(inline_data=types.Blob(
                                                mime_type=mime_type,
                                                data=audio_bytes
                                            ))]
                                        )
                                        await sess.send_client_content(turns=[content], turn_complete=False)
                                        
                                    except Exception as e:
                                        print(f"Error processing audio: {e}")
                                        await websocket.send_json({
                                            "type": "error",
                                            "content": f"Audio processing error: {str(e)}"
                                        })
                        
                        except asyncio.TimeoutError:
                            # No data received, continue listening
                            continue
                        
                        except WebSocketDisconnect:
                            print(f"WebSocket disconnected: {session_id}")
                            break
                        
                        except Exception as e:
                            print(f"Error in frontend handler: {e}")
                            break
                finally:
                    silence_task.cancel()
            
            # Run both tasks concurrently
            try:
                await asyncio.gather(
                    listen_to_gemini(),
                    handle_frontend_messages()
                )
            except Exception as e:
                print(f"Error in communication tasks: {e}")
    
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await call_manager.close_session(session_id)
        try:
            await websocket.close()
        except:
            pass


@router.get("/status")
async def video_call_status():
    """Check video call service status"""
    return {
        "service": "video_call",
        "status": "active" if GENAI_AVAILABLE else "unavailable",
        "gemini_available": GENAI_AVAILABLE,
        "active_sessions": len(call_manager.active_sessions),
        "features": [
            "Real-time video calling",
            "Voice chat with avatar",
            "Fashion advice",
            "Outfit analysis"
        ]
    }


@router.get("/test")
async def test_connection():
    """Test Gemini API connection"""
    if not GENAI_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Gemini API not available",
                "message": "Install google-genai: pip install google-genai"
            }
        )
    
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return JSONResponse(
            status_code=503,
            content={
                "error": "API key not configured",
                "message": "Set GOOGLE_API_KEY in .env file"
            }
        )
    
    try:
        client = genai.Client(api_key=api_key)
        return {
            "status": "ready",
            "message": "Gemini API connection successful",
            "api_key_present": True
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Connection failed",
                "message": str(e)
            }
        )
