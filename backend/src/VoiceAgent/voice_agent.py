"""
Voice Agent with Gemini Live API

Handles voice interaction and feature navigation commands.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
import base64
from typing import Optional, Callable, Dict, Any
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/voice-agent", tags=["Voice Agent"])

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# Define tools for feature navigation (Gemini format)
NAVIGATION_TOOLS = [
    {
        "function_declarations": [
            {
                "name": "open_video_call",
                "description": "Opens the video call feature to have a face-to-face conversation with the virtual boyfriend",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "open_virtual_tryon",
                "description": "Opens the virtual try-on feature to see how clothes look on the user",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "open_photobooth",
                "description": "Opens the photobooth feature to take photos with the virtual boyfriend",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "open_shop",
                "description": "Opens the shopping feature to search for and buy clothes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Optional search query for what to shop for"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "open_recommendations",
                "description": "Opens the outfit recommendations feature for AI-powered style advice",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "open_calendar",
                "description": "Opens the calendar to view upcoming events and plan outfits",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "open_wardrobe",
                "description": "Opens the wardrobe/profile to view saved clothes and outfits",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    }
]


@router.websocket("/ws")
async def voice_agent_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for voice agent with Gemini Live API

    Receives audio chunks from frontend, sends to Gemini Live API,
    and returns both text transcriptions and audio responses.
    """
    print(f"[Voice Agent] WebSocket connection attempt from: {websocket.client}")
    print(f"[Voice Agent] Origin: {websocket.headers.get('origin')}")
    print(f"[Voice Agent] Host: {websocket.headers.get('host')}")

    # Accept WebSocket connection
    try:
        await websocket.accept()
        print("[Voice Agent] WebSocket accepted successfully")
    except Exception as e:
        print(f"[Voice Agent] Accept failed: {e}")
        import traceback
        traceback.print_exc()
        return
    print("Voice agent WebSocket connected")
    
    # System instruction for the voice agent
    system_instruction = """You are a helpful and friendly virtual boyfriend assistant for Lovelace, 
a fashion app. You help users with their wardrobe, style, and shopping needs.

You can:
- Have casual conversations about fashion and style
- Help users navigate the app by opening features
- Give fashion advice and outfit recommendations
- Be supportive and encouraging

When users ask to do something, use the appropriate tool to open that feature.
Be conversational, friendly, and helpful. Keep responses concise for voice interaction."""

    try:
        # Initialize Gemini Live API session
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            system_instruction=system_instruction,
            tools=NAVIGATION_TOOLS
        )
        
        # Start chat session
        chat = model.start_chat(history=[])
        
        # Send welcome message
        await websocket.send_json({
            "type": "text",
            "content": "Hey! I'm here to help. Just talk to me naturally!"
        })
        
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "audio":
                    # Audio chunk from user
                    audio_base64 = data.get("data")
                    
                    # Decode audio
                    audio_bytes = base64.b64decode(audio_base64)
                    
                    # TODO: Process audio with Gemini Live API
                    # For now, send acknowledgment
                    await websocket.send_json({
                        "type": "status",
                        "content": "Processing audio..."
                    })
                    
                elif message_type == "text":
                    # Text message from user
                    user_message = data.get("content")
                    
                    # Send to Gemini
                    response = await asyncio.to_thread(
                        chat.send_message,
                        user_message
                    )
                    
                    # Check for function calls
                    if response.candidates[0].content.parts:
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                function_call = part.function_call
                                await websocket.send_json({
                                    "type": "function_call",
                                    "function": function_call.name,
                                    "args": dict(function_call.args) if function_call.args else {}
                                })
                    
                    # Send text response
                    response_text = response.text if hasattr(response, 'text') else ""
                    if response_text:
                        await websocket.send_json({
                            "type": "text",
                            "content": response_text
                        })
                        
                        # TODO: Generate audio response with TTS
                        # For now, just send text
                    
                elif message_type == "start_recording":
                    await websocket.send_json({
                        "type": "status",
                        "content": "Listening..."
                    })
                    
                elif message_type == "stop_recording":
                    await websocket.send_json({
                        "type": "status",
                        "content": "Processing..."
                    })
                    
            except WebSocketDisconnect:
                print("Voice agent WebSocket disconnected")
                break
            except Exception as e:
                print(f"Error in voice agent loop: {e}")
                await websocket.send_json({
                    "type": "error",
                    "content": str(e)
                })
                
    except Exception as e:
        print(f"Voice agent error: {e}")
        await websocket.send_json({
            "type": "error",
            "content": "Failed to initialize voice agent"
        })
    finally:
        await websocket.close()
        print("Voice agent WebSocket closed")
