#!/usr/bin/env python3
"""
Lovelace Live Video Call - Interactive Demo Script

This script provides an interactive way to test the Gemini Live API integration
with various scenarios and configurations.

Usage:
    python demo.py                  # Run all demos
    python demo.py --text           # Text conversation only
    python demo.py --tools          # Test tool/function calling
    python demo.py --audio-config   # Show audio configuration
    python demo.py --interactive    # Interactive mode
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add parent directory (backend/src) to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Change to script directory to ensure relative paths work
os.chdir(current_dir)

# Load .env from project root
try:
    from dotenv import load_dotenv
    # Navigate up to project root (LiveVideoCall -> src -> backend -> root)
    project_root = current_dir.parent.parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        # Don't print in demo.py to keep output clean
    else:
        print(f"⚠️  .env file not found at: {env_path}")
except ImportError:
    pass  # Silently skip if dotenv not installed

try:
    from live_video_call import (
        GeminiLiveSession,
        LiveVideoCallManager,
        SessionConfig,
        ResponseModality,
        VoiceName,
        demo_text_conversation,
        demo_with_tools,
        demo_audio_conversation,
        run_all_demos
    )
    from google.genai import types
except ImportError as e:
    print(f"Error: Could not import LiveVideoCall module: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}")
    print("\nTroubleshooting:")
    print("1. Make sure you have google-genai installed: pip install google-genai")
    print("2. Make sure python-dotenv is installed: pip install python-dotenv")
    print("3. Try running from backend/src/LiveVideoCall: cd backend/src/LiveVideoCall && python demo.py")
    sys.exit(1)


async def interactive_mode():
    """Interactive chat mode with the virtual boyfriend"""
    print("\n" + "="*60)
    print("INTERACTIVE MODE - Chat with Virtual Boyfriend")
    print("="*60)
    print("\nCommands:")
    print("  'quit' or 'exit' - Exit interactive mode")
    print("  'history' - Show conversation history")
    print("  'clear' - Clear screen")
    print("  'voice <name>' - Change voice (kore, charon, fenrir)")
    print("="*60 + "\n")
    
    # Create session
    config = SessionConfig(
        user_id="interactive_user",
        response_modality=ResponseModality.TEXT,
        enable_video=False,
        enable_audio=False,
        temperature=0.9  # More creative responses
    )
    
    manager = LiveVideoCallManager()
    
    try:
        print("Connecting to Gemini Live API...")
        session_id = await manager.create_session("interactive_user", config)
        session = await manager.get_session(session_id)
        
        if not session:
            print("Failed to create session")
            return
        
        print("✓ Connected! Start chatting with your virtual boyfriend.\n")
        
        async with session.session as sess:
            while True:
                # Get user input
                try:
                    user_input = input("👤 You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n\nExiting...")
                    break
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit']:
                    print("Goodbye! 👋")
                    break
                
                elif user_input.lower() == 'history':
                    history = session.get_conversation_history()
                    print("\n" + "="*60)
                    print("CONVERSATION HISTORY")
                    print("="*60)
                    for msg in history:
                        role_icon = "👤" if msg["role"] == "user" else "🤖"
                        print(f"\n{role_icon} {msg['role'].title()}: {msg['content']}")
                    print("="*60 + "\n")
                    continue
                
                elif user_input.lower() == 'clear':
                    print("\n" * 50)
                    continue
                
                elif user_input.lower().startswith('voice '):
                    voice_name = user_input.split()[1].upper()
                    print(f"Note: Voice changes require reconnection (not implemented in demo)")
                    continue
                
                # Send message
                content = types.Content(parts=[types.Part(text=user_input)])
                await sess.send_client_content(turns=[content], turn_complete=True)
                
                # Receive response
                print("🤖 Lovelace: ", end="", flush=True)
                response_text = ""
                
                async for response in sess.receive():
                    if hasattr(response, 'text') and response.text:
                        print(response.text, end="", flush=True)
                        response_text += response.text
                    
                    # Check for tool calls
                    if hasattr(response, 'tool_call'):
                        tool_info = response.tool_call
                        print(f"\n  [🔧 Using tool: {tool_info.get('name', 'unknown')}]")
                    
                    # Check for turn completion
                    if hasattr(response, 'server_content') and response.server_content:
                        if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                            break
                
                print()  # New line after response
                
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await manager.close_all_sessions()


async def quick_test():
    """Quick test to verify API connection"""
    print("\n" + "="*60)
    print("QUICK TEST - API Connection")
    print("="*60 + "\n")
    
    config = SessionConfig(
        user_id="test_user",
        response_modality=ResponseModality.TEXT,
        enable_video=False,
        enable_audio=False
    )
    
    session = GeminiLiveSession(config)
    
    try:
        print("Testing connection...")
        connected = await session.connect()
        
        if connected:
            print("✅ SUCCESS - Gemini Live API is working!")
            print(f"   Status: {session.status.value}")
            print(f"   Model: gemini-2.0-flash-exp")
            
            # Quick message test
            async with session.session as sess:
                # Use the correct content format
                content = types.Content(
                    parts=[types.Part(text="Hi! Just testing. Say hello in one sentence.")]
                )
                await sess.send_client_content(turns=[content], turn_complete=True)
                print("\n   Testing message exchange...")
                
                async for response in sess.receive():
                    if hasattr(response, 'text') and response.text:
                        print(f"   Response: {response.text[:100]}...")
                        break
            
            print("\n✅ All systems operational!")
        else:
            print("❌ FAILED - Could not connect to API")
            print("   Check your API key in .env file")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await session.close()


async def scenario_demo():
    """Demo specific scenarios relevant to Lovelace"""
    print("\n" + "="*60)
    print("SCENARIO DEMOS - Virtual Boyfriend Use Cases")
    print("="*60 + "\n")
    
    scenarios = [
        {
            "name": "Morning Outfit Check",
            "messages": [
                "Good morning! I need help picking an outfit for work today.",
                "It's going to be sunny and warm, around 75°F.",
                "I'm thinking light colors. What do you suggest?"
            ]
        },
        {
            "name": "Date Night Preparation",
            "messages": [
                "I have a date tonight! Can you help me look amazing?",
                "We're going to a nice Italian restaurant.",
                "Should I wear a dress or go with jeans and a nice top?"
            ]
        },
        {
            "name": "Wardrobe Review",
            "messages": [
                "I feel like my wardrobe needs an update.",
                "Can you tell me what basic pieces I should have?",
                "My style is casual chic, mostly neutrals."
            ]
        }
    ]
    
    manager = LiveVideoCallManager()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'─'*60}")
        print(f"Scenario {i}: {scenario['name']}")
        print('─'*60 + "\n")
        
        try:
            # Create session for scenario
            config = SessionConfig(
                user_id=f"scenario_{i}",
                response_modality=ResponseModality.TEXT,
                enable_video=False,
                enable_audio=False
            )
            
            session_id = await manager.create_session(f"scenario_{i}", config)
            session = await manager.get_session(session_id)
            
            if not session:
                print("Failed to create session")
                continue
            
            async with session.session as sess:
                for msg in scenario['messages']:
                    print(f"👤 You: {msg}")
                    content = types.Content(parts=[types.Part(text=msg)])
                    await sess.send_client_content(turns=[content], turn_complete=True)
                    
                    print("🤖 Lovelace: ", end="", flush=True)
                    async for response in sess.receive():
                        if hasattr(response, 'text') and response.text:
                            print(response.text, end="", flush=True)
                        
                        if hasattr(response, 'server_content') and response.server_content:
                            if hasattr(response.server_content, 'turn_complete') and response.server_content.turn_complete:
                                break
                    print("\n")
                    await asyncio.sleep(1)
            
            await manager.close_session(session_id)
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"✗ Scenario failed: {e}")
    
    await manager.close_all_sessions()
    print("\n" + "="*60)
    print("All scenarios completed!")
    print("="*60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Lovelace Live Video Call Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python demo.py                  Run all demos
    python demo.py --quick          Quick API test
    python demo.py --interactive    Interactive chat mode
    python demo.py --scenarios      Run scenario demos
    python demo.py --text           Text conversation demo
    python demo.py --tools          Tool calling demo
        """
    )
    
    parser.add_argument('--quick', action='store_true', help='Quick API connection test')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive chat mode')
    parser.add_argument('--scenarios', '-s', action='store_true', help='Run scenario demos')
    parser.add_argument('--text', action='store_true', help='Text conversation demo')
    parser.add_argument('--tools', action='store_true', help='Tool calling demo')
    parser.add_argument('--audio-config', action='store_true', help='Audio configuration demo')
    
    args = parser.parse_args()
    
    # Check if any specific demo was requested
    if args.quick:
        asyncio.run(quick_test())
    elif args.interactive:
        asyncio.run(interactive_mode())
    elif args.scenarios:
        asyncio.run(scenario_demo())
    elif args.text:
        asyncio.run(demo_text_conversation())
    elif args.tools:
        asyncio.run(demo_with_tools())
    elif args.audio_config:
        asyncio.run(demo_audio_conversation())
    else:
        # Run all demos
        print("No specific demo selected. Running all demos...")
        print("Use --help to see available options\n")
        asyncio.run(run_all_demos())


if __name__ == "__main__":
    main()
