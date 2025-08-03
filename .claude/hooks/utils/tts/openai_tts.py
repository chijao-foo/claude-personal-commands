# /// script
# dependencies = ["openai"]
# ///

import os
import sys
import tempfile
import subprocess
from openai import OpenAI
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from env_loader import get_env_var

def speak_openai(text, voice=None):
    """
    Convert text to speech using OpenAI TTS API
    """
    api_key = get_env_var("OPENAI_API_KEY")
    voice = voice or get_env_var("OPENAI_TTS_VOICE", "alloy")
    if not api_key:
        return False, "OPENAI_API_KEY not set"
    
    try:
        client = OpenAI(api_key=api_key)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Save to temporary file and play
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(response.content)
            tmp_file.flush()
            
            # Try to play the audio file
            try:
                if sys.platform == "win32":
                    subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{tmp_file.name}').PlaySync()"], 
                                 check=True, capture_output=True)
                elif sys.platform == "darwin":
                    subprocess.run(["afplay", tmp_file.name], check=True, capture_output=True)
                else:
                    subprocess.run(["mpg123", tmp_file.name], check=True, capture_output=True)
                
                return True, "Success"
            except subprocess.CalledProcessError as e:
                return False, f"Audio playback failed: {e}"
            finally:
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass
                    
    except Exception as e:
        return False, f"OpenAI TTS error: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python openai_tts.py 'text to speak'")
        sys.exit(1)
    
    text = sys.argv[1]
    success, message = speak_openai(text)
    
    if success:
        print(f"OpenAI TTS: {message}")
    else:
        print(f"OpenAI TTS failed: {message}", file=sys.stderr)
        sys.exit(1)