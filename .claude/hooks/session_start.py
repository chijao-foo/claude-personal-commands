# /// script
# dependencies = []
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

def get_git_context():
    """Get git status and branch information"""
    context = {}
    
    try:
        # Get current branch
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            context['branch'] = result.stdout.strip()
        
        # Get git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            modified_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            context['modified_files'] = len(modified_files)
            context['status'] = 'clean' if not modified_files else 'modified'
        
        # Get recent commits
        result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            context['recent_commits'] = result.stdout.strip().split('\n')[:3]
        
    except Exception as e:
        context['error'] = str(e)
    
    return context

def load_claude_md():
    """Load CLAUDE.md if it exists"""
    claude_file = Path("CLAUDE.md")
    if claude_file.exists():
        try:
            with open(claude_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    return None

def load_context_files():
    """Load additional context files if they exist"""
    context_files = {}
    
    common_files = [
        "README.md",
        "package.json",
        "requirements.txt",
        "Cargo.toml",
        "go.mod",
        ".claude/context.md"
    ]
    
    for file_name in common_files:
        file_path = Path(file_name)
        if file_path.exists() and file_path.stat().st_size < 10000:  # Max 10KB
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    context_files[file_name] = f.read()
            except Exception:
                continue
    
    return context_files

def inject_development_context():
    """Inject development context for Claude"""
    context_lines = []
    
    # Add session info
    context_lines.append("=== Development Session Context ===")
    context_lines.append(f"Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Add git context
    git_context = get_git_context()
    if 'branch' in git_context:
        context_lines.append(f"Git Branch: {git_context['branch']}")
    if 'status' in git_context:
        context_lines.append(f"Git Status: {git_context['status']}")
        if git_context['status'] == 'modified':
            context_lines.append(f"Modified Files: {git_context['modified_files']}")
    
    # Add recent commits
    if 'recent_commits' in git_context:
        context_lines.append("Recent Commits:")
        for commit in git_context['recent_commits']:
            context_lines.append(f"  - {commit}")
    
    # Add engineer name
    engineer_name = get_env_var("ENGINEER_NAME")
    if engineer_name:
        context_lines.append(f"Engineer: {engineer_name}")
    
    # Add project directory
    context_lines.append(f"Working Directory: {os.getcwd()}")
    
    context_lines.append("=== End Context ===\n")
    
    return context_lines

def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        source = input_data.get("source", "unknown")
        session_id = input_data.get("session_id", "unknown")
        
        # Ensure log directory exists
        log_dir = ensure_log_dir()
        log_file = log_dir / "session_start.json"
        
        # Load existing logs
        log_data = load_existing_logs(log_file)
        
        # Get development context
        git_context = get_git_context()
        claude_md = load_claude_md()
        context_files = load_context_files()
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "source": source,
            "git_context": git_context,
            "claude_md_found": claude_md is not None,
            "context_files": list(context_files.keys())
        }
        
        # Check command line arguments
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # Inject context if --context flag is present
        if "--context" in args:
            context_lines = inject_development_context()
            for line in context_lines:
                print(line)
            
            log_entry["context_injected"] = True
        
        # Load CLAUDE.md if --claude-md flag is present
        if "--claude-md" in args and claude_md:
            print("=== CLAUDE.md Content ===")
            print(claude_md)
            print("=== End CLAUDE.md ===\n")
            log_entry["claude_md_loaded"] = True
        
        log_data.append(log_entry)
        
        # Save updated logs
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Optional verbose output
        if "--verbose" in args:
            print(f"✓ Session started: {source}", file=sys.stderr)
    
    except Exception as e:
        print(f"SessionStart hook error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()