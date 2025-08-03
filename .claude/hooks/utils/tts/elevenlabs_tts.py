# /// script
# dependencies = ["requests"]
# ///

import os
import sys
import requests
import tempfile
import subprocess
import json
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from env_loader import get_env_var

def speak_elevenlabs(text, voice_id=None):
    """
    Convert text to speech using ElevenLabs API
    """
    api_key = get_env_var("ELEVENLABS_API_KEY")
    voice_id = voice_id or get_env_var("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    if not api_key:
        return False, "ELEVENLABS_API_KEY not set"
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        
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
                    
    except requests.RequestException as e:
        return False, f"ElevenLabs API error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python elevenlabs_tts.py 'text to speak'")
        sys.exit(1)
    
    text = sys.argv[1]
    success, message = speak_elevenlabs(text)
    
    if success:
        print(f"ElevenLabs TTS: {message}")
    else:
        print(f"ElevenLabs TTS failed: {message}", file=sys.stderr)
        sys.exit(1)