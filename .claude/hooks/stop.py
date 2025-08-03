# /// script
# dependencies = ["requests", "openai", "anthropic", "pyttsx3"]
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

def generate_ai_completion_message():
    """Generate AI completion message with fallback"""
    try:
        # Try OpenAI first
        if get_env_var("OPENAI_API_KEY"):
            result = subprocess.run([
                "uv", "run", ".claude/hooks/utils/llm/openai_completion.py"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
        
        # Try Anthropic second
        if get_env_var("ANTHROPIC_API_KEY"):
            result = subprocess.run([
                "uv", "run", ".claude/hooks/utils/llm/anthropic_completion.py"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
        
        # Fallback to static messages
        fallback_messages = [
            "Task completed successfully!",
            "All done! Ready for next task.",
            "Execution finished. Standing by.",
            "Task wrapped up nicely.",
            "Ready for your next request!"
        ]
        import random
        return random.choice(fallback_messages)
        
    except Exception:
        return "Task completed!"

def play_completion_sound(message):
    """Play TTS completion message"""
    try:
        engineer_name = get_env_var("ENGINEER_NAME")
        
        # Use intelligent TTS
        result = subprocess.run([
            "uv", "run", ".claude/hooks/utils/tts/intelligent_tts.py", 
            message, engineer_name or ""
        ], capture_output=True, text=True, timeout=30)
        
        return result.returncode == 0
        
    except Exception:
        return False

def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        session_id = input_data.get("session_id", "unknown")
        stop_hook_active = input_data.get("stop_hook_active", False)
        
        # Ensure log directory exists
        log_dir = ensure_log_dir()
        log_file = log_dir / "stop.json"
        
        # Load existing logs
        log_data = load_existing_logs(log_file)
        
        # Check command line arguments
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # Generate AI completion message if --ai flag is present
        completion_message = "Task completed!"
        if "--ai" in args:
            completion_message = generate_ai_completion_message()
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "stop_hook_active": stop_hook_active,
            "completion_message": completion_message
        }
        
        # Play TTS if --tts flag is present
        if "--tts" in args:
            tts_success = play_completion_sound(completion_message)
            log_entry["tts"] = {
                "enabled": True,
                "success": tts_success,
                "message": completion_message
            }
            
            if tts_success and "--verbose" in args:
                print(f"🔊 Completion: {completion_message}", file=sys.stderr)
        else:
            log_entry["tts"] = {"enabled": False}
        
        log_data.append(log_entry)
        
        # Save updated logs
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Optional verbose output
        if "--verbose" in args:
            print(f"✓ Stop logged: {completion_message}", file=sys.stderr)
        
        # Show completion message to user
        if "--show-message" in args:
            print(f"🎉 {completion_message}")
    
    except Exception as e:
        print(f"Stop hook error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()