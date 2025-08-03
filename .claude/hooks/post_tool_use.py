# /// script
# dependencies = []
# ///

import sys
import json
import os
from datetime import datetime
from pathlib import Path

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

def convert_chat_transcript():
    """Convert JSONL transcript to readable JSON format"""
    try:
        # Find the most recent JSONL file in projects directory
        projects_dir = Path.home() / ".claude" / "projects"
        if not projects_dir.exists():
            return False, "No projects directory found"
        
        jsonl_files = list(projects_dir.glob("**/*.jsonl"))
        if not jsonl_files:
            return False, "No JSONL files found"
        
        # Get the most recent file
        latest_file = max(jsonl_files, key=lambda f: f.stat().st_mtime)
        
        # Read JSONL and convert to readable format
        chat_data = []
        with open(latest_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        chat_data.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        # Save to chat.json
        log_dir = ensure_log_dir()
        chat_file = log_dir / "chat.json"
        
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)
        
        return True, f"Converted {len(chat_data)} entries to chat.json"
        
    except Exception as e:
        return False, f"Chat conversion error: {e}"

def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})
        session_id = input_data.get("session_id", "unknown")
        
        # Ensure log directory exists
        log_dir = ensure_log_dir()
        log_file = log_dir / "post_tool_use.json"
        
        # Load existing logs
        log_data = load_existing_logs(log_file)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_response": tool_response,
            "success": tool_response.get("success", True)
        }
        
        log_data.append(log_entry)
        
        # Save updated logs
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Check command line arguments
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # Convert chat transcript if --chat flag is present
        if "--chat" in args:
            success, message = convert_chat_transcript()
            log_entry["chat_conversion"] = {"success": success, "message": message}
            
            # Re-save with chat conversion info
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            if success and "--verbose" in args:
                print(f"✓ {message}", file=sys.stderr)
        
        # Optional verbose output
        if "--verbose" in args:
            print(f"✓ Tool completed: {tool_name}", file=sys.stderr)
    
    except Exception as e:
        print(f"PostToolUse hook error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()