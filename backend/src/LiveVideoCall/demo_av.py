#!/usr/bin/env python3
"""
Lovelace Live Video Call - Audio/Video Demo

This demo captures real audio and video from your microphone and webcam,
streaming it to Gemini Live API for real-time interaction with the virtual boyfriend.

Requirements:
    pip install pyaudio opencv-python numpy

Usage:
    python demo_av.py                # Audio + Video
    python demo_av.py --audio-only   # Audio only (no camera)
    python demo_av.py --test-devices # List available devices
"""

import asyncio
import argparse
import sys
import os
import threading
import queue
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
os.chdir(current_dir)

# Load .env from project root
try:
    from dotenv import load_dotenv
    # Navigate up to project root (backend/src/LiveVideoCall -> backend/src -> backend -> root)
    project_root = current_dir.parent.parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded .env from: {project_root}")
    else:
        print(f"⚠️  .env file not found at: {env_path}")
        print("   Make sure you have GOOGLE_API_KEY set in your .env file")
except ImportError:
    print("⚠️  python-dotenv not installed")
    print("   Install with: pip install python-dotenv")

try:
    from live_video_call import (
        GeminiLiveSession,
        SessionConfig,
        ResponseModality,
        VoiceName,
    )
    from google.genai import types
except ImportError as e:
    print(f"Error: Could not import required modules: {e}")
    sys.exit(1)

try:
    import pyaudio
    import wave
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️  PyAudio not installed. Install with: pip install pyaudio")
    print("   On Windows, you may need: pip install pipwin && pipwin install pyaudio")

try:
    import cv2
    import numpy as np
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False
    print("⚠️  OpenCV not installed. Install with: pip install opencv-python")

# Audio configuration
AUDIO_FORMAT = pyaudio.paInt16 if AUDIO_AVAILABLE else None
AUDIO_CHANNELS = 1
AUDIO_RATE = 16000  # 16kHz as required by Gemini
AUDIO_CHUNK = 1024

# Video configuration
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 2  # Lower FPS to reduce API costs


class AudioVideoCapture:
    """Captures audio and video streams"""
    
    def __init__(self, enable_audio=True, enable_video=True):
        self.enable_audio = enable_audio and AUDIO_AVAILABLE
        self.enable_video = enable_video and VIDEO_AVAILABLE
        
        self.audio_stream = None
        self.video_capture = None
        self.is_running = False
        
        self.audio_queue = queue.Queue()
        self.video_queue = queue.Queue()
        
        if not self.enable_audio and not self.enable_video:
            raise ValueError("At least one of audio or video must be enabled")
    
    def start(self):
        """Start capturing audio and video"""
        self.is_running = True
        
        # Start audio capture
        if self.enable_audio:
            try:
                audio = pyaudio.PyAudio()
                self.audio_stream = audio.open(
                    format=AUDIO_FORMAT,
                    channels=AUDIO_CHANNELS,
                    rate=AUDIO_RATE,
                    input=True,
                    frames_per_buffer=AUDIO_CHUNK,
                    stream_callback=self._audio_callback
                )
                self.audio_stream.start_stream()
                print(f"✓ Audio capture started (16kHz, mono)")
            except Exception as e:
                print(f"✗ Failed to start audio: {e}")
                self.enable_audio = False
        
        # Start video capture
        if self.enable_video:
            try:
                self.video_capture = cv2.VideoCapture(0)
                self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
                self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
                self.video_capture.set(cv2.CAP_PROP_FPS, VIDEO_FPS)
                
                # Test if camera works
                ret, frame = self.video_capture.read()
                if not ret:
                    raise Exception("Failed to read from camera")
                
                print(f"✓ Video capture started ({VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps)")
                
                # Start video thread
                self.video_thread = threading.Thread(target=self._video_loop, daemon=True)
                self.video_thread.start()
            except Exception as e:
                print(f"✗ Failed to start video: {e}")
                self.enable_video = False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        if self.is_running:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def _video_loop(self):
        """Video capture loop"""
        import time
        frame_delay = 1.0 / VIDEO_FPS
        
        while self.is_running and self.video_capture.isOpened():
            ret, frame = self.video_capture.read()
            if ret:
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                self.video_queue.put(buffer.tobytes())
            
            time.sleep(frame_delay)
    
    def get_audio_chunk(self, timeout=0.1):
        """Get next audio chunk"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_video_frame(self, timeout=0.1):
        """Get next video frame"""
        try:
            return self.video_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop capturing"""
        self.is_running = False
        
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        
        if self.video_capture:
            self.video_capture.release()
        
        # Clear queues
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.video_queue.empty():
            try:
                self.video_queue.get_nowait()
            except queue.Empty:
                break
        
        print("Capture stopped")


class AudioPlayer:
    """Plays audio responses from the model"""
    
    def __init__(self):
        if not AUDIO_AVAILABLE:
            raise ImportError("PyAudio not available")
        
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,  # Gemini outputs 24kHz
            output=True
        )
        print("✓ Audio playback ready")
    
    def play(self, audio_data: bytes):
        """Play audio data"""
        try:
            self.stream.write(audio_data)
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def close(self):
        """Close audio player"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()


async def live_av_demo(enable_audio=True, enable_video=True):
    """
    Live audio/video demo with Gemini Live API
    """
    print("\n" + "="*70)
    print("LIVE AUDIO/VIDEO DEMO - Virtual Boyfriend")
    print("="*70)
    print("\nThis demo will:")
    if enable_audio:
        print("  • Capture audio from your microphone")
        print("  • Send it to Gemini Live API")
        print("  • Play back the avatar's voice responses")
    if enable_video:
        print("  • Capture video from your webcam")
        print("  • Let the avatar see you and your outfits")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: No API key found!")
        print()
        print("Please set GOOGLE_API_KEY in your .env file (project root)")
        print("Get your key at: https://aistudio.google.com/app/apikey")
        return
    
    # Check requirements
    if enable_audio and not AUDIO_AVAILABLE:
        print("❌ PyAudio not installed. Cannot capture audio.")
        return
    
    if enable_video and not VIDEO_AVAILABLE:
        print("❌ OpenCV not installed. Cannot capture video.")
        return
    
    # Create session config
    config = SessionConfig(
        user_id="av_demo_user",
        response_modality=ResponseModality.AUDIO if enable_audio else ResponseModality.TEXT,
        voice_name=VoiceName.KORE,
        enable_video=enable_video,
        enable_audio=enable_audio,
        system_instruction="""You are a charming, fashion-savvy virtual boyfriend. 
        You can see the user through their camera and hear them speak. 
        Comment on what you see - their outfit, surroundings, expressions.
        Be warm, supportive, and give specific fashion advice.
        Keep responses conversational and natural."""
    )
    
    # Create session
    print("Connecting to Gemini Live API...")
    session = GeminiLiveSession(config)
    
    try:
        connected = await session.connect()
        if not connected:
            print("❌ Failed to connect to API")
            return
        
        print("✓ Connected to Gemini Live API")
        print()
        
        # Start capture
        capture = AudioVideoCapture(enable_audio=enable_audio, enable_video=enable_video)
        capture.start()
        
        # Start audio player if using audio
        player = None
        if enable_audio:
            try:
                player = AudioPlayer()
            except Exception as e:
                print(f"Warning: Could not initialize audio player: {e}")
        
        # Send initial greeting
        print("Sending initial message...")
        async with session.session as sess:
            greeting = types.Content(
                parts=[types.Part(text="Hi! I can see and hear you now. Tell me about your outfit!")]
            )
            await sess.send_client_content(turns=[greeting], turn_complete=True)
            
            print("\n🎤 Listening... (speak naturally, I can hear you!)")
            if enable_video:
                print("📹 Camera active (I can see you!)")
            print()
            
            # Streaming loop
            response_text = ""
            audio_chunks_sent = 0
            video_frames_sent = 0
            
            try:
                while True:
                    # Send audio chunks
                    if enable_audio:
                        audio_chunk = capture.get_audio_chunk(timeout=0.01)
                        if audio_chunk:
                            # Create audio blob with correct format
                            audio_blob = types.Blob(
                                data=audio_chunk,
                                mime_type="audio/pcm;rate=16000"
                            )
                            await sess.send_realtime_input(audio=audio_blob)
                            audio_chunks_sent += 1
                            if audio_chunks_sent % 50 == 0:
                                print(f"  [Sent {audio_chunks_sent} audio chunks]", end="\r")
                    
                    # Send video frames (less frequently)
                    if enable_video and video_frames_sent < 1000:  # Limit frames to control cost
                        video_frame = capture.get_video_frame(timeout=0.01)
                        if video_frame:
                            # Create image blob
                            image_blob = types.Blob(
                                data=video_frame,
                                mime_type="image/jpeg"
                            )
                            # Note: Video support may be limited in current SDK
                            try:
                                await sess.send_realtime_input(image=image_blob)
                                video_frames_sent += 1
                                if video_frames_sent % 5 == 0:
                                    print(f"  [Sent {video_frames_sent} video frames]", end="\r")
                            except TypeError:
                                # Video input might not be supported yet
                                if video_frames_sent == 0:
                                    print("\n⚠️  Video input not supported in current API, continuing with audio only...")
                                pass
                    
                    # Receive responses (non-blocking)
                    try:
                        async for response in sess.receive():
                            # Handle text responses
                            if hasattr(response, 'text') and response.text:
                                print(f"\n🤖 {response.text}")
                                response_text += response.text
                            
                            # Handle audio responses
                            if hasattr(response, 'data') and response.data and player:
                                player.play(response.data)
                            
                            # Check for turn completion
                            if hasattr(response, 'server_content') and response.server_content:
                                if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                                    print("\n🎤 Listening...")
                                    break
                    except asyncio.TimeoutError:
                        pass
                    
                    await asyncio.sleep(0.01)
                    
            except KeyboardInterrupt:
                print("\n\nStopping...")
        
        print(f"\n\nSession stats:")
        print(f"  Audio chunks sent: {audio_chunks_sent}")
        print(f"  Video frames sent: {video_frames_sent}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        capture.stop()
        if player:
            player.close()
        await session.close()
        print("\n✓ Demo completed")


def test_devices():
    """Test and list available audio/video devices"""
    print("\n" + "="*70)
    print("DEVICE TEST")
    print("="*70 + "\n")
    
    # Test audio devices
    if AUDIO_AVAILABLE:
        print("Audio Devices:")
        audio = pyaudio.PyAudio()
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  [{i}] {info['name']}")
                print(f"      Sample Rate: {info['defaultSampleRate']}")
                print(f"      Channels: {info['maxInputChannels']}")
        audio.terminate()
    else:
        print("❌ PyAudio not available")
    
    print()
    
    # Test video devices
    if VIDEO_AVAILABLE:
        print("Video Devices:")
        for i in range(5):  # Check first 5 indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    h, w = frame.shape[:2]
                    print(f"  [Camera {i}] Resolution: {w}x{h}")
                cap.release()
        
        if not cv2.VideoCapture(0).isOpened():
            print("  ❌ No camera detected")
    else:
        print("❌ OpenCV not available")
    
    print("\n" + "="*70)


def check_requirements():
    """Check if all requirements are installed"""
    print("\n" + "="*70)
    print("REQUIREMENTS CHECK")
    print("="*70 + "\n")
    
    all_good = True
    
    # Check PyAudio
    if AUDIO_AVAILABLE:
        print("✓ PyAudio installed")
    else:
        print("❌ PyAudio NOT installed")
        print("   Install: pip install pyaudio")
        print("   Windows: pip install pipwin && pipwin install pyaudio")
        all_good = False
    
    # Check OpenCV
    if VIDEO_AVAILABLE:
        print("✓ OpenCV installed")
    else:
        print("❌ OpenCV NOT installed")
        print("   Install: pip install opencv-python")
        all_good = False
    
    # Check numpy
    try:
        import numpy
        print("✓ NumPy installed")
    except ImportError:
        print("❌ NumPy NOT installed")
        print("   Install: pip install numpy")
        all_good = False
    
    print()
    
    if all_good:
        print("✅ All requirements satisfied!")
    else:
        print("⚠️  Please install missing requirements")
    
    print("="*70 + "\n")
    
    return all_good


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Lovelace Live A/V Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument('--audio-only', action='store_true', help='Use audio only (no video)')
    parser.add_argument('--video-only', action='store_true', help='Use video only (no audio)')
    parser.add_argument('--test-devices', action='store_true', help='Test audio/video devices')
    parser.add_argument('--check-requirements', action='store_true', help='Check if requirements are installed')
    
    args = parser.parse_args()
    
    # Check requirements
    if args.check_requirements:
        check_requirements()
        return
    
    # Test devices
    if args.test_devices:
        test_devices()
        return
    
    # Determine what to enable
    enable_audio = not args.video_only
    enable_video = not args.audio_only
    
    # Check if requirements are met
    if enable_audio and not AUDIO_AVAILABLE:
        print("❌ PyAudio not installed. Cannot use audio.")
        print("   Install: pip install pyaudio")
        print("   Or use --video-only flag")
        return
    
    if enable_video and not VIDEO_AVAILABLE:
        print("❌ OpenCV not installed. Cannot use video.")
        print("   Install: pip install opencv-python")
        print("   Or use --audio-only flag")
        return
    
    # Run demo
    asyncio.run(live_av_demo(enable_audio=enable_audio, enable_video=enable_video))


if __name__ == "__main__":
    main()
