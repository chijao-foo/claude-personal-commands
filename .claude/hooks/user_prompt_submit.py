# /// script
# dependencies = ["requests"]
# ///

import sys
import json
import os
import re
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

def validate_prompt(prompt):
    """Validate prompt for security issues"""
    dangerous_patterns = [
        (r'rm\s+.*-[rf]', 'Dangerous rm command detected'),
        (r'sudo\s+rm', 'Dangerous sudo rm command'),
        (r'>\s*/etc/', 'System directory write attempt'),
        (r'curl.*\|\s*sh', 'Dangerous pipe to shell'),
        (r'api[_-]?key\s*[=:]\s*["\']?[a-zA-Z0-9]+', 'Potential API key exposure'),
        (r'password\s*[=:]\s*["\']?[a-zA-Z0-9]+', 'Potential password exposure'),
    ]
    
    prompt_lower = prompt.lower()
    
    for pattern, reason in dangerous_patterns:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            return False, reason
    
    return True, None

def inject_context():
    """Inject helpful project context"""
    context_lines = []
    
    # Add timestamp
    context_lines.append(f"Session Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Add git status if available
    try:
        import subprocess
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            if result.stdout.strip():
                context_lines.append(f"Git Status: Modified files detected")
            else:
                context_lines.append(f"Git Status: Clean working directory")
        
        # Get current branch
        branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                     capture_output=True, text=True, timeout=5)
        if branch_result.returncode == 0:
            context_lines.append(f"Git Branch: {branch_result.stdout.strip()}")
    except:
        pass
    
    # Add engineer name if available
    engineer_name = get_env_var("ENGINEER_NAME")
    if engineer_name:
        context_lines.append(f"Engineer: {engineer_name}")
    
    return context_lines

def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        prompt = input_data.get("prompt", "")
        session_id = input_data.get("session_id", "unknown")
        
        # Ensure log directory exists
        log_dir = ensure_log_dir()
        log_file = log_dir / "user_prompt_submit.json"
        
        # Load existing logs
        log_data = load_existing_logs(log_file)
        
        # Add new log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "prompt": prompt,
            "prompt_length": len(prompt)
        }
        
        # Check command line arguments for behavior
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # Validate prompt if --validate flag is present
        if "--validate" in args:
            is_valid, reason = validate_prompt(prompt)
            log_entry["validation"] = {"valid": is_valid, "reason": reason}
            
            if not is_valid:
                print(f"BLOCKED: {reason}", file=sys.stderr)
                log_entry["status"] = "blocked"
                log_data.append(log_entry)
                
                # Save log
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
                
                sys.exit(2)  # Block the prompt
        
        # Inject context if --context flag is present
        if "--context" in args:
            context_lines = inject_context()
            if context_lines:
                print("=== Session Context ===")
                for line in context_lines:
                    print(line)
                print("=== End Context ===\n")
                log_entry["context_injected"] = True
        
        log_entry["status"] = "processed"
        log_data.append(log_entry)
        
        # Save updated logs
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Log to stdout for transcript
        if "--verbose" in args:
            print(f"✓ Prompt logged: {len(prompt)} characters", file=sys.stderr)
    
    except Exception as e:
        print(f"UserPromptSubmit hook error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()