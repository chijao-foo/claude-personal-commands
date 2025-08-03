# /// script
# dependencies = []
# ///

import os
from pathlib import Path

def load_dotenv():
    """
    Load environment variables from .env file
    Searches for .env in current directory and parent directories
    """
    def find_env_file():
        """Find .env file in current or parent directories"""
        current_dir = Path.cwd()
        
        # Check current directory first
        env_file = current_dir / ".env"
        if env_file.exists():
            return env_file
        
        # Check parent directories up to root
        for parent in current_dir.parents:
            env_file = parent / ".env"
            if env_file.exists():
                return env_file
        
        return None
    
    def parse_env_line(line):
        """Parse a single line from .env file"""
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            return None, None
        
        # Split on first = sign
        if '=' not in line:
            return None, None
        
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        
        return key, value
    
    env_file = find_env_file()
    if not env_file:
        return False, "No .env file found"
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        loaded_vars = []
        for line in lines:
            key, value = parse_env_line(line)
            if key and value:
                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value
                    loaded_vars.append(key)
        
        return True, f"Loaded {len(loaded_vars)} variables from {env_file.name}"
        
    except Exception as e:
        return False, f"Error loading .env file: {e}"

def get_env_var(key, default=None):
    """
    Get environment variable with fallback to .env file
    """
    # Try to load .env if variable not found
    if key not in os.environ:
        load_dotenv()
    
    return os.environ.get(key, default)

if __name__ == "__main__":
    success, message = load_dotenv()
    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")