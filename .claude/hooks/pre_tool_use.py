# /// script
# dependencies = []
# ///

import sys
import json
import os
import re
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

def is_dangerous_command(tool_name, tool_input):
    """Check if command is dangerous and should be blocked"""
    if tool_name != "Bash":
        return False, None
    
    command = tool_input.get("command", "")
    
    # Dangerous patterns
    dangerous_patterns = [
        (r'rm\s+.*-[rf].*/', 'Dangerous rm -rf command with path'),
        (r'sudo\s+rm', 'Dangerous sudo rm command'),
        (r'chmod\s+777', 'Dangerous permission change'),
        (r'>\s*/etc/', 'Writing to system directories'),
        (r'curl.*\|\s*sh', 'Dangerous pipe to shell'),
        (r'wget.*\|\s*sh', 'Dangerous pipe to shell'),
        (r'dd\s+if=', 'Potentially dangerous dd command'),
        (r'mkfs\.', 'Filesystem creation command'),
        (r'fdisk', 'Disk partitioning command'),
    ]
    
    for pattern, reason in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True, reason
    
    return False, None

def is_sensitive_file_access(tool_name, tool_input):
    """Check if accessing sensitive files"""
    sensitive_files = ['.env', '.env.local', '.env.production', 'secrets.json', 'config/secrets', 'id_rsa', 'id_ecdsa']
    
    if tool_name in ["Read", "Write", "Edit"]:
        file_path = tool_input.get("file_path", "")
        for sensitive in sensitive_files:
            if sensitive in file_path.lower():
                return True, f"Access to sensitive file: {sensitive}"
    
    return False, None

def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        session_id = input_data.get("session_id", "unknown")
        
        # Ensure log directory exists
        log_dir = ensure_log_dir()
        log_file = log_dir / "pre_tool_use.json"
        
        # Load existing logs
        log_data = load_existing_logs(log_file)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "tool_name": tool_name,
            "tool_input": tool_input
        }
        
        # Check for dangerous commands
        is_dangerous, danger_reason = is_dangerous_command(tool_name, tool_input)
        if is_dangerous:
            # Check if user has pre-approved dangerous commands via flag file
            approval_file = Path(".claude/allow_dangerous")
            if approval_file.exists():
                print(f"⚠️  SECURITY WARNING: {danger_reason} (pre-approved)", file=sys.stderr)
                log_entry["status"] = "approved_dangerous_preauth"
                log_entry["warning_reason"] = danger_reason
            else:
                command = tool_input.get("command", "")
                print(f"\n⚠️  SECURITY WARNING: {danger_reason}", file=sys.stderr)
                print(f"Command: {command}", file=sys.stderr)
                print("To allow dangerous commands, run: touch .claude/allow_dangerous", file=sys.stderr)
                print("To allow just once, use: /danger-allow", file=sys.stderr)
                log_entry["status"] = "blocked"
                log_entry["block_reason"] = danger_reason
                log_data.append(log_entry)
                
                # Save log
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                
                sys.exit(2)  # Block the tool execution
        
        # Check for sensitive file access
        is_sensitive, sensitive_reason = is_sensitive_file_access(tool_name, tool_input)
        if is_sensitive:
            print(f"BLOCKED: {sensitive_reason}", file=sys.stderr)
            log_entry["status"] = "blocked"
            log_entry["block_reason"] = sensitive_reason
            log_data.append(log_entry)
            
            # Save log
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            sys.exit(2)  # Block the tool execution
        
        log_entry["status"] = "approved"
        log_data.append(log_entry)
        
        # Save updated logs
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Optional verbose output
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        if "--verbose" in args:
            print(f"✓ Tool approved: {tool_name}", file=sys.stderr)
    
    except Exception as e:
        print(f"PreToolUse hook error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()