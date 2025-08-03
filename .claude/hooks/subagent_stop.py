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

def get_tts_setting():
    """Get TTS enabled status from settings"""
    settings_file = Path(".claude/settings.local.json")
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            return settings.get('tts_enabled', True)
        except:
            return True
    return True

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

def play_subagent_completion():
    """Play TTS for subagent completion"""
    try:
        engineer_name = get_env_var("ENGINEER_NAME")
        message = "Subagent Complete"
        
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
        log_file = log_dir / "subagent_stop.json"
        
        # Load existing logs
        log_data = load_existing_logs(log_file)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "stop_hook_active": stop_hook_active
        }
        
        # Check command line arguments
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # Play TTS if --tts flag is present and not disabled by user
        tts_enabled = get_tts_setting()
        if "--tts" in args and tts_enabled:
            tts_success = play_subagent_completion()
            log_entry["tts"] = {
                "enabled": True,
                "success": tts_success,
                "message": "Subagent Complete"
            }
            
            if tts_success and "--verbose" in args:
                print("🔊 Subagent Complete", file=sys.stderr)
        else:
            log_entry["tts"] = {
                "enabled": False,
                "reason": "disabled_by_user" if not tts_enabled else "flag_not_set"
            }
        
        log_data.append(log_entry)
        
        # Save updated logs
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Optional verbose output
        if "--verbose" in args:
            print("✓ Subagent stop logged", file=sys.stderr)
    
    except Exception as e:
        print(f"SubagentStop hook error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()