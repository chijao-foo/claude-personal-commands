# 🎯 Post-Installation Checklist

## ✅ Installation Complete!

Your Claude Code hooks are now installed with full TTS support. Follow this checklist to activate all features:

---

## 🔑 Required: API Keys & Environment Setup

### **1. Configure .env File (Recommended)**

Your API keys are stored securely in a `.env` file that won't be committed to git:

```bash
# Edit the .env file with your API keys
# Open .env in your editor and add your keys
```

The `.env` file template is already created with these fields:
```bash
# TTS Providers (choose one or both)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# AI Completion (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Personalization
ENGINEER_NAME=YourName
```

### **2. Alternative: Shell Environment Variables**

If you prefer shell exports, add to your profile (`.bashrc`, `.zshrc`):

```bash
export ELEVENLABS_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"
export ENGINEER_NAME="YourName"
```

**Note:** .env file takes precedence over shell variables.

### **3. Get API Keys**

#### **ElevenLabs (Premium TTS) - Recommended**
- 🌐 Sign up: https://elevenlabs.io/
- 🔑 Get API key: https://elevenlabs.io/app/settings/api-keys
- 💰 Cost: ~$5/month for moderate usage
- ⭐ Best voice quality and natural speech

#### **OpenAI (High Quality TTS) - Alternative**
- 🌐 Sign up: https://openai.com/
- 🔑 Get API key: https://platform.openai.com/api-keys
- 💰 Cost: Pay-per-use (~$0.015 per 1K characters)
- ⭐ Good quality, widely available

#### **System TTS (Free Fallback)**
- ✅ Already installed with `pyttsx3`
- 💰 Cost: Free
- ⭐ Basic quality, always works

---

## 🧪 Testing Your Installation

### **1. Test UV and Dependencies**
```bash
# Test UV is working
uv --version

# Test TTS utilities (will auto-install dependencies)
uv run .claude/hooks/utils/tts/system_tts.py "Testing system TTS"
```

### **2. Test API Connections (after adding keys to .env)**
```bash
# Test .env file loading
uv run .claude/hooks/utils/env_loader.py

# Test ElevenLabs (if API key in .env)
uv run .claude/hooks/utils/tts/elevenlabs_tts.py "Testing ElevenLabs"

# Test OpenAI TTS (if API key in .env)
uv run .claude/hooks/utils/tts/openai_tts.py "Testing OpenAI TTS"

# Test intelligent TTS (tries all methods)
uv run .claude/hooks/utils/tts/intelligent_tts.py "Testing intelligent TTS"
```

### **3. Test Hooks with Claude Code**
```bash
# Start a Claude Code session to trigger SessionStart hook
claude

# Try a simple prompt to trigger UserPromptSubmit hook
> What files are in this directory?

# Check logs were created
ls .claude/logs/
```

---

## 🎛️ Configuration Options

### **Minimal Setup (No TTS)**
Edit `.claude/settings.json` to disable TTS:

```json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "uv run .claude/hooks/user_prompt_submit.py --log-only"}]}],
    "PreToolUse": [{"hooks": [{"type": "command", "command": "uv run .claude/hooks/pre_tool_use.py"}]}],
    "SessionStart": [{"hooks": [{"type": "command", "command": "uv run .claude/hooks/session_start.py --context"}]}]
  }
}
```

### **Security-Only Setup**
```json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "uv run .claude/hooks/user_prompt_submit.py --validate"}]}],
    "PreToolUse": [{"hooks": [{"type": "command", "command": "uv run .claude/hooks/pre_tool_use.py"}]}]
  }
}
```

### **Full Production Setup** (Current)
- All hooks enabled with TTS
- Complete logging and audit trails
- AI-generated completion messages
- Automatic context injection

---

## 🔧 Troubleshooting

### **"uv: command not found"**
```bash
# Add UV to PATH
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc

# Or reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### **Audio Not Playing**
```bash
# Windows: Install Windows Media Feature Pack
# macOS: Should work out of box
# Linux: Install audio player
sudo apt install mpg123  # Ubuntu/Debian
sudo yum install mpg123  # CentOS/RHEL
```

### **API Key Errors**
```bash
# Check environment variables are set
echo $ELEVENLABS_API_KEY
echo $OPENAI_API_KEY

# Test API connectivity
curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/user
```

### **Permission Errors**
```bash
# Make hook files executable
chmod +x .claude/hooks/*.py
chmod +x .claude/hooks/utils/tts/*.py
chmod +x .claude/hooks/utils/llm/*.py
```

### **Dependency Issues**
```bash
# Clear UV cache and reinstall
uv cache clean
uv run .claude/hooks/user_prompt_submit.py --help
```

---

## 📋 Optional Enhancements

### **1. Copy to Global Claude Directory**
Make hooks available in all projects:
```bash
# Copy hook system to global Claude directory
cp -r .claude ~/.claude/global-hooks

# Reference in other projects
ln -s ~/.claude/global-hooks .claude
```

### **2. Add Project-Specific Context**
Create `.claude/context.md` with project-specific information:
```markdown
# Project Context

## Architecture
- Frontend: React/TypeScript
- Backend: Node.js/Express  
- Database: PostgreSQL

## Key Files
- API routes: `/src/routes/`
- Components: `/src/components/`
- Tests: `/tests/`

## Development Notes
- Use ESLint for code style
- Jest for testing
- Prettier for formatting
```

### **3. Custom Git Hooks Integration**
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Log commit attempts
echo "$(date): Pre-commit triggered" >> .claude/logs/git_activity.log
```

---

## 📊 Monitoring & Logs

### **Log Locations**
```bash
.claude/logs/
├── user_prompt_submit.json    # All prompts
├── pre_tool_use.json         # Security blocks
├── post_tool_use.json        # Tool executions  
├── stop.json                 # Completions
├── session_start.json        # Session info
├── notification.json         # Notifications
├── subagent_stop.json       # Sub-agent events
├── pre_compact.json         # Compaction events
└── chat.json                # Readable transcript
```

### **Log Analysis Commands**
```bash
# Count total prompts today
cat .claude/logs/user_prompt_submit.json | jq '[.[] | select(.timestamp | startswith("2024-01-20"))] | length'

# Show blocked commands
cat .claude/logs/pre_tool_use.json | jq '.[] | select(.status == "blocked")'

# Show completion messages
cat .claude/logs/stop.json | jq '.[] | .completion_message'
```

---

## 🎉 You're All Set!

Your Claude Code environment now has:

✅ **Complete Security** - Multi-layer protection  
✅ **Smart Context** - Auto-loads project info  
✅ **Audio Feedback** - TTS for all major events  
✅ **Full Logging** - Complete audit trails  
✅ **AI Enhancement** - Intelligent completion messages  

**Next Steps:**
1. Set your API keys for TTS
2. Test with a simple Claude session
3. Customize flags in `.claude/settings.json` as needed
4. Monitor logs in `.claude/logs/` for insights

**Get Support:**
- 📖 Read: `.claude/CLAUDE_HOOKS_GUIDE.md`
- 🔍 Check logs: `.claude/logs/`
- 🐛 Report issues: Include log files for debugging

Happy coding with your enhanced Claude Code environment! 🚀