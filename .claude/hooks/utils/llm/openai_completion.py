# /// script
# dependencies = ["openai"]
# ///

import os
import sys
import json
from openai import OpenAI
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from env_loader import get_env_var

def generate_completion_message(tool_name=None, session_context=None):
    """
    Generate AI completion message using OpenAI
    """
    api_key = get_env_var("OPENAI_API_KEY")
    if not api_key:
        return False, "OPENAI_API_KEY not set"
    
    try:
        client = OpenAI(api_key=api_key)
        
        prompt = "Generate a brief, friendly completion message for a coding assistant. "
        if tool_name:
            prompt += f"The last tool used was {tool_name}. "
        prompt += "Keep it under 10 words, professional but encouraging."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant that generates brief completion messages."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        message = response.choices[0].message.content.strip()
        return True, message
        
    except Exception as e:
        return False, f"OpenAI completion error: {e}"

if __name__ == "__main__":
    tool_name = sys.argv[1] if len(sys.argv) > 1 else None
    success, message = generate_completion_message(tool_name)
    
    if success:
        print(message)
    else:
        print("Task completed successfully!", file=sys.stderr)
        sys.exit(1)