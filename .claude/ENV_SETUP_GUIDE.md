# 🔑 .env File Setup Guide

Your Claude Code hooks now use a `.env` file for secure API key management.

## 📁 Files Created

✅ **`.env`** - Your API keys (edit this file)  
✅ **`.env.example`** - Template with all available options  
✅ **`.gitignore`** - Updated to exclude `.env` from git  

## 🚀 Quick Setup

### **1. Edit Your .env File**

Open `.env` in your editor and add your API keys:

```bash
# Required for TTS (choose one or both)
ELEVENLABS_API_KEY=el-your-actual-api-key-here
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Optional for AI completion messages  
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional personalization
ENGINEER_NAME=YourName
```

### **2. Test the Setup**

```bash
# Test .env loading
uv run .claude/hooks/utils/env_loader.py

# Test TTS with your keys
uv run .claude/hooks/utils/tts/intelligent_tts.py "Testing .env setup"
```

## 🔧 How It Works

The hooks automatically:
1. **Search for .env** - Looks in current directory and parent directories
2. **Load variables** - Only if not already set in environment  
3. **Fallback gracefully** - Works with or without API keys
4. **Stay secure** - .env is excluded from git commits

## 🛡️ Security Features

✅ **Git ignored** - `.env` won't be committed  
✅ **Local priority** - Environment variables override .env  
✅ **Auto-discovery** - Finds .env in project root or parents  
✅ **Fallback system** - Works without API keys (system TTS)  

## 📝 Available Variables

### **TTS Providers**
```bash
ELEVENLABS_API_KEY=     # Premium quality TTS
OPENAI_API_KEY=         # High quality TTS + AI
ELEVENLABS_VOICE_ID=    # Optional: specific voice
OPENAI_TTS_VOICE=       # Optional: alloy, echo, fable, etc.
```

### **AI Completion**
```bash
ANTHROPIC_API_KEY=      # For AI-generated completion messages
OPENAI_API_KEY=         # Also used for AI completions
```

### **Personalization**
```bash
ENGINEER_NAME=          # Your name for TTS messages
HOOKS_DEBUG=           # true/false for debug logging
```

## 🔄 Migration from Shell Variables

If you previously set environment variables in your shell:

1. **Copy values to .env** - Move from shell to .env file
2. **Remove shell exports** - Optional, .env takes precedence  
3. **Test functionality** - Verify hooks still work

## 🆘 Troubleshooting

### **"No .env file found"**
- Check you're in the right directory
- Verify `.env` file exists (not `.env.example`)

### **"API key not working"**
```bash
# Debug: Check if .env is loaded
uv run .claude/hooks/utils/env_loader.py

# Check specific variable
echo $ELEVENLABS_API_KEY  # May be empty if only in .env
```

### **"Variables not loading"**
- Check .env syntax: `KEY=value` (no spaces around =)
- Remove quotes if not needed: `KEY=value` not `KEY="value"`
- Check file permissions: `chmod 600 .env`

### **"Git is tracking .env"**
```bash
# Remove from git if accidentally added
git rm --cached .env
git commit -m "Remove .env from tracking"
```

## ✨ Benefits of .env Setup

🔒 **Secure** - Keys stay local, never committed  
🎯 **Convenient** - One file for all projects  
🔄 **Portable** - Easy to copy between machines  
📁 **Organized** - All config in one place  
🚀 **No setup** - Works immediately after adding keys  

Your Claude Code hooks are now using secure .env configuration!