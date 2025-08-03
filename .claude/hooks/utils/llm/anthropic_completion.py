# /// script
# dependencies = ["anthropic"]
# ///

import os
import sys
import json
import anthropic
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from env_loader import get_env_var

def generate_completion_message(tool_name=None, session_context=None):
    """
    Generate AI completion message using Anthropic Claude
    """
    api_key = get_env_var("ANTHROPIC_API_KEY")
    if not api_key:
        return False, "ANTHROPIC_API_KEY not set"
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = "Generate a brief, friendly completion message for a coding assistant. "
        if tool_name:
            prompt += f"The last tool used was {tool_name}. "
        prompt += "Keep it under 10 words, professional but encouraging."
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        message = response.content[0].text.strip()
        return True, message
        
    except Exception as e:
        return False, f"Anthropic completion error: {e}"

if __name__ == "__main__":
    tool_name = sys.argv[1] if len(sys.argv) > 1 else None
    success, message = generate_completion_message(tool_name)
    
    if success:
        print(message)
    else:
        print("Task completed successfully!", file=sys.stderr)
        sys.exit(1)