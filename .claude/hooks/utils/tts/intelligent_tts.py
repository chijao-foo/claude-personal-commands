# /// script
# dependencies = ["requests", "openai", "pyttsx3"]
# ///

import os
import sys
import subprocess
import random
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from env_loader import get_env_var

def speak_intelligent(text, engineer_name=None):
    """
    Intelligent TTS with fallback priority: ElevenLabs > OpenAI > System
    Adds engineer name 30% of the time for personalization
    """
    # Add engineer name randomly (30% chance)
    if engineer_name and random.random() < 0.3:
        text = f"{engineer_name}, {text}"
    
    # Try ElevenLabs first
    if get_env_var("ELEVENLABS_API_KEY"):
        try:
            result = subprocess.run([
                "uv", "run", ".claude/hooks/utils/tts/elevenlabs_tts.py", text
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"🔊 ElevenLabs: {text}")
                return True, "ElevenLabs success"
        except Exception as e:
            print(f"ElevenLabs failed: {e}", file=sys.stderr)
    
    # Try OpenAI second
    if get_env_var("OPENAI_API_KEY"):
        try:
            result = subprocess.run([
                "uv", "run", ".claude/hooks/utils/tts/openai_tts.py", text
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"🔊 OpenAI: {text}")
                return True, "OpenAI success"
        except Exception as e:
            print(f"OpenAI TTS failed: {e}", file=sys.stderr)
    
    # Fall back to system TTS
    try:
        result = subprocess.run([
            "uv", "run", ".claude/hooks/utils/tts/system_tts.py", text
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"🔊 System: {text}")
            return True, "System TTS success"
    except Exception as e:
        print(f"System TTS failed: {e}", file=sys.stderr)
    
    return False, "All TTS methods failed"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python intelligent_tts.py 'text to speak' [engineer_name]")
        sys.exit(1)
    
    text = sys.argv[1]
    engineer_name = sys.argv[2] if len(sys.argv) > 2 else get_env_var("ENGINEER_NAME")
    
    success, message = speak_intelligent(text, engineer_name)
    
    if not success:
        print(f"TTS failed: {message}", file=sys.stderr)
        sys.exit(1)