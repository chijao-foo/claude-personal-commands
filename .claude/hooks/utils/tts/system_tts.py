# /// script
# dependencies = ["pyttsx3"]
# ///

import sys
import pyttsx3

def speak_system(text, rate=200):
    """
    Convert text to speech using system TTS (pyttsx3)
    """
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        engine.say(text)
        engine.runAndWait()
        return True, "Success"
    except Exception as e:
        return False, f"System TTS error: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python system_tts.py 'text to speak'")
        sys.exit(1)
    
    text = sys.argv[1]
    success, message = speak_system(text)
    
    if success:
        print(f"System TTS: {message}")
    else:
        print(f"System TTS failed: {message}", file=sys.stderr)
        sys.exit(1)