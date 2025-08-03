# /// script
# dependencies = ["requests", "openai", "pyttsx3"]
# ///

import sys
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))
from env_loader import get_env_var

def ensure_log_dir():
    """Ensure logs directory exists"""
    log_dir = Path(".claude/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def load_existing_logs(log_file):
    """Load existing log data"""
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def play_notification_sound(message):
    """Play TTS notification"""
    try:
        # Add engineer name context
        engineer_name = get_env_var("ENGINEER_NAME")
        
        # Different messages based on notification type
        if "input" in message.lower() or "waiting" in message.lower():
            tts_message = "Your agent needs your input"
        elif "error" in message.lower():
            tts_message = "Agent encountered an error"
        elif "complete" in message.lower():
            tts_message = "Agent task completed"
        else:
            tts_message = "Agent notification"
        
        # Use intelligent TTS
        result = subprocess.run([
            "uv", "run", ".claude/hooks/utils/tts/intelligent_tts.py", 
            tts_message, engineer_name or ""
        ], capture_output=True, text=True, timeout=30)
        
        return result.returncode == 0, tts_message
        
    except Exception as e:
        return False, f"TTS error: {e}"

def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        message = input_data.get("message", "")
        session_id = input_data.get("session_id", "unknown")
        
        # Ensure log directory exists
        log_dir = ensure_log_dir()
        log_file = log_dir / "notification.json"
        
        # Load existing logs
        log_data = load_existing_logs(log_file)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "message": message
        }
        
        # Check command line arguments
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # Play TTS notification if --notify flag is present
        if "--notify" in args:
            tts_success, tts_message = play_notification_sound(message)
            log_entry["tts"] = {
                "enabled": True,
                "success": tts_success,
                "message": tts_message
            }
            
            if tts_success and "--verbose" in args:
                print(f"🔊 Notification: {tts_message}", file=sys.stderr)
        else:
            log_entry["tts"] = {"enabled": False}
        
        log_data.append(log_entry)
        
        # Save updated logs
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Optional verbose output
        if "--verbose" in args:
            print(f"✓ Notification logged: {message[:50]}...", file=sys.stderr)
    
    except Exception as e:
        print(f"Notification hook error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()