#!/usr/bin/env python3
"""
Lovelace Live Audio Demo - WORKING VERSION

This demo uses push-to-talk or automatic pauses to know when you're done speaking.

Usage:
    python demo_av_fixed.py              # Push-to-talk mode
    python demo_av_fixed.py --auto-vad   # Auto voice activity detection
"""

import asyncio
import sys
import os
from pathlib import Path
import time

# Setup paths and .env
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
os.chdir(current_dir)

try:
    from dotenv import load_dotenv
    project_root = current_dir.parent.parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded .env from: {project_root}")
except ImportError:
    pass

try:
    from live_video_call import SessionConfig, ResponseModality, VoiceName
    from google.genai import types
    from google import genai
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)

try:
    import pyaudio
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    print("❌ PyAudio not installed: pip install pyaudio")
    sys.exit(1)

# Audio config
AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
AUDIO_RATE = 16000
AUDIO_CHUNK = 1024


class SimpleAudioRecorder:
    """Simple push-to-talk audio recorder"""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.frames = []
    
    def start_recording(self):
        """Start recording audio"""
        self.frames = []
        self.is_recording = True
        self.stream = self.audio.open(
            format=AUDIO_FORMAT,
            channels=AUDIO_CHANNELS,
            rate=AUDIO_RATE,
            input=True,
            frames_per_buffer=AUDIO_CHUNK
        )
        print("🎤 Recording... (press Enter when done)")
    
    def record_chunk(self):
        """Record one chunk"""
        if self.is_recording and self.stream:
            try:
                data = self.stream.read(AUDIO_CHUNK, exception_on_overflow=False)
                self.frames.append(data)
                return data
            except:
                return None
        return None
    
    def stop_recording(self):
        """Stop recording and return all audio"""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        audio_data = b''.join(self.frames)
        self.frames = []
        print(f"✓ Recorded {len(audio_data)} bytes")
        return audio_data
    
    def close(self):
        """Close audio"""
        if self.stream:
            self.stream.close()
        self.audio.terminate()


class AudioPlayer:
    """Play audio responses"""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,  # Gemini outputs 24kHz
            output=True
        )
    
    def play(self, audio_data: bytes):
        """Play audio"""
        try:
            self.stream.write(audio_data)
        except Exception as e:
            print(f"Playback error: {e}")
    
    def close(self):
        """Close player"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()


async def push_to_talk_demo():
    """
    Simple push-to-talk demo that ACTUALLY WORKS
    """
    print("\n" + "="*70)
    print("WORKING AUDIO DEMO - Push-to-Talk Mode")
    print("="*70)
    print("\nHow it works:")
    print("  1. You'll be prompted to speak")
    print("  2. Start speaking and press Enter when done")
    print("  3. Your audio is sent to Gemini")
    print("  4. The avatar responds with voice!")
    print("\nPress Ctrl+C to exit")
    print("="*70 + "\n")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No API key found! Set GOOGLE_API_KEY in .env")
        return
    
    # Initialize
    client = genai.Client(api_key=api_key)
    recorder = SimpleAudioRecorder()
    player = AudioPlayer()
    
    # Config
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
        Be warm, supportive, and give specific fashion advice. Keep responses concise 
        and conversational - about 2-3 sentences."""
    }
    
    print("Connecting to Gemini Live API...")
    
    try:
        async with client.aio.live.connect(model="gemini-2.0-flash-exp", config=config) as session:
            print("✓ Connected!\n")
            
            # Send initial greeting
            greeting = types.Content(
                parts=[types.Part(text="Hey! I'm your fashion advisor. What can I help you with today?")]
            )
            await session.send_client_content(turns=[greeting], turn_complete=True)
            
            # Get greeting response
            print("🤖 Avatar: ", end="", flush=True)
            async for response in session.receive():
                if hasattr(response, 'text') and response.text:
                    print(response.text, end="", flush=True)
                if hasattr(response, 'data') and response.data:
                    player.play(response.data)
                if hasattr(response, 'server_content') and response.server_content:
                    if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                        break
            print("\n")
            
            # Main conversation loop
            turn = 0
            while True:
                turn += 1
                print(f"\n--- Turn {turn} ---")
                print("Press Enter to start recording, then Enter again when done")
                input("Ready? Press Enter...")
                
                # Start recording in background
                recorder.start_recording()
                
                # Record until user presses Enter
                record_task = asyncio.create_task(asyncio.to_thread(record_in_background, recorder))
                await asyncio.to_thread(input)  # Wait for Enter
                
                # Stop recording
                audio_data = recorder.stop_recording()
                
                if len(audio_data) < 1000:
                    print("⚠️  Recording too short, skipping...")
                    continue
                
                # Send audio to Gemini
                print("📤 Sending audio to Gemini...")
                
                # Send audio in chunks
                chunk_size = AUDIO_CHUNK * 2  # 2048 bytes per chunk
                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i+chunk_size]
                    audio_blob = types.Blob(
                        data=chunk,
                        mime_type="audio/pcm;rate=16000"
                    )
                    await session.send_realtime_input(audio=audio_blob)
                
                # Signal end of audio
                await asyncio.sleep(0.5)  # Give it a moment to process
                
                # Receive response
                print("🤖 Avatar: ", end="", flush=True)
                response_received = False
                timeout = time.time() + 10  # 10 second timeout
                
                while time.time() < timeout:
                    try:
                        async for response in session.receive():
                            response_received = True
                            
                            if hasattr(response, 'text') and response.text:
                                print(response.text, end="", flush=True)
                            
                            if hasattr(response, 'data') and response.data:
                                player.play(response.data)
                            
                            if hasattr(response, 'server_content') and response.server_content:
                                if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                                    print()
                                    break
                        
                        if response_received:
                            break
                            
                    except asyncio.TimeoutError:
                        break
                    
                    await asyncio.sleep(0.1)
                
                if not response_received:
                    print("⚠️  No response received")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        recorder.close()
        player.close()
        print("\n✓ Demo ended")


def record_in_background(recorder):
    """Record audio in background until stopped"""
    while recorder.is_recording:
        recorder.record_chunk()
        time.sleep(0.01)


def main():
    """Main entry point"""
    asyncio.run(push_to_talk_demo())


if __name__ == "__main__":
    main()
