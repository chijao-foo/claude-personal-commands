# /// script
# dependencies = []
# ///

import sys
import json
import os
import shutil
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

def backup_chat_transcript():
    """Backup chat transcript before compaction"""
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
        
        # Create backup directory
        backup_dir = Path(".claude/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"transcript_backup_{timestamp}.jsonl"
        
        # Copy the file
        shutil.copy2(latest_file, backup_file)
        
        return True, f"Backed up to {backup_file.name}"
        
    except Exception as e:
        return False, f"Backup error: {e}"

def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        trigger = input_data.get("trigger", "unknown")
        custom_instructions = input_data.get("custom_instructions", "")
        session_id = input_data.get("session_id", "unknown")
        
        # Ensure log directory exists
        log_dir = ensure_log_dir()
        log_file = log_dir / "pre_compact.json"
        
        # Load existing logs
        log_data = load_existing_logs(log_file)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "trigger": trigger,
            "custom_instructions": custom_instructions
        }
        
        # Check command line arguments
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # Backup transcript if --backup flag is present
        if "--backup" in args:
            backup_success, backup_message = backup_chat_transcript()
            log_entry["backup"] = {
                "enabled": True,
                "success": backup_success,
                "message": backup_message
            }
            
            if backup_success and "--verbose" in args:
                print(f"💾 Backup: {backup_message}", file=sys.stderr)
        else:
            log_entry["backup"] = {"enabled": False}
        
        log_data.append(log_entry)
        
        # Save updated logs
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Provide feedback for manual compaction
        if trigger == "manual" and "--verbose" in args:
            print(f"🗜️ Manual compaction triggered", file=sys.stderr)
            if custom_instructions:
                print(f"📝 Instructions: {custom_instructions[:100]}...", file=sys.stderr)
        
        # Optional verbose output
        if "--verbose" in args:
            print(f"✓ Pre-compact logged: {trigger}", file=sys.stderr)
    
    except Exception as e:
        print(f"PreCompact hook error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()