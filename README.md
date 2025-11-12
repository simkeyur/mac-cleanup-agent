# Mac Cleanup Agent 🧹

An intelligent Python agent that automatically organizes files in your Downloads, Documents, and Desktop folders. Files are organized by year and type using both rule-based classification and AI-powered classification via Ollama.

## Features

- 📁 **Smart Organization**: Organizes files into `year/type` folder structure
- 🤖 **AI-Powered**: Uses Ollama for intelligent file classification
- 🧹 **Cache Cleanup**: Automatically cleans system caches (Homebrew, pip, npm, VS Code)
- ⚙️ **Configurable**: Easy YAML configuration with model switching
- 🔒 **Safe**: Dry-run mode and file age filters to prevent accidents
- 📊 **Comprehensive Logging**: Track all operations with detailed logs
- 🗑️ **Log Rotation**: Automatic 7-day rolling log retention
- ⏰ **Automation Ready**: Perfect for SwiftBar scheduled execution

## Structure

Organized files follow this pattern:
```
~/Documents/Organized/
├── 2024/
│   ├── images/
│   ├── documents/
│   ├── videos/
│   └── misc/
└── 2025/
    ├── images/
    ├── documents/
    └── misc/
```

## Installation

1. **Clone or navigate to the project directory**:
```bash
cd /Users/simkeyur/src/local-agents/mac-cleanup-agent
```

2. **Create a virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Install Ollama** (if not already installed):
   - Download from [ollama.ai](https://ollama.ai)
   - Install a model: `ollama pull llama3.2`

## Configuration

Edit `config.yaml` to customize:

### Ollama Settings
```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "llama3.2"  # Change to any installed model
  temperature: 0.3
  timeout: 30
```

### Folders to Organize
```yaml
folders:
  - "~/Downloads"
  - "~/Documents"
  - "~/Desktop"
```

### Organization Settings
```yaml
organization:
  base_path: "~/Documents/Organized"
  structure: "year/type"
  misc_folder: "misc"
```

### Safety Settings
```yaml
safety:
  dry_run: false  # Set true to preview without moving
  min_age_days: 0  # Only organize files older than X days
  exclude_patterns:
    - ".DS_Store"
    - ".git"
```

### Cache Cleanup Settings
```yaml
cache_cleanup:
  enabled:
    - "homebrew"      # Homebrew package cache (~2-4GB)
    - "pip"           # Python pip cache (~50MB)
    - "npm"           # Node.js npm cache (if installed)
    - "vscode"        # VS Code cache (~600MB-1GB)
    - "user_caches"   # Safe user caches (python, node-gyp)
    # Optional browser cache cleanup (uncomment to enable):
    # - "chrome"      # Google Chrome cache (~1GB+)
    # - "safari"      # Safari cache
    # - "firefox"     # Firefox cache
```

**Note**: Browser cache cleanup will clear browsing data and may log you out of websites. Enable only if needed.

## Usage

### Basic Usage

Run the agent to organize files AND clean caches:
```bash
python3 main.py
```

### Cache Cleanup Only

Clean system caches without organizing files:
```bash
python3 main.py --cache-only --dry-run  # Preview
python3 main.py --cache-only            # Actually clean
```

### Skip Cache Cleanup

Organize files only, skip cache cleanup:
```bash
python3 main.py --skip-cache-cleanup
```

### Dry Run (Preview)

Preview what would be organized without moving files:
```bash
python3 main.py --dry-run
```

### Organize Specific Folder

Organize only a specific folder:
```bash
python3 main.py --folder ~/Downloads
```

### Disable AI Classification

Use only rule-based classification:
```bash
python3 main.py --no-ai
```

### Custom Config File

Use a different configuration file:
```bash
python3 main.py --config my-config.yaml
```

## SwiftBar Automation

[SwiftBar](https://swiftbar.app) is a macOS menu bar app that can run scripts on a schedule. Here's how to automate the cleanup agent:

### 1. Install SwiftBar

```bash
brew install swiftbar
```

### 2. Create SwiftBar Script

Create a script in your SwiftBar plugin folder (e.g., `~/.swiftbar/cleanup-agent.1h.sh`):

```bash
#!/bin/bash
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.refreshOnOpen>true</swiftbar.refreshOnOpen>

# Metadata
# <swiftbar.title>Cleanup Agent</swiftbar.title>
# <swiftbar.version>v1.0</swiftbar.version>
# <swiftbar.author>Your Name</swiftbar.author>
# <swiftbar.desc>Organize Downloads, Documents, and Desktop files</swiftbar.desc>

# Configuration
AGENT_PATH="/Users/simkeyur/src/local-agents/mac-cleanup-agent"
VENV_PATH="$AGENT_PATH/venv"
LOG_FILE="$AGENT_PATH/cleanup_agent.log"

# Menu bar icon
echo "🧹"
echo "---"

# Menu options
echo "Run Cleanup Now | bash='$0' param1=run terminal=false refresh=true"
echo "Dry Run (Preview) | bash='$0' param1=dry-run terminal=true"
echo "View Logs | bash='tail' param1='-f' param2='$LOG_FILE' terminal=true"
echo "---"
echo "Open Organized Folder | bash='open' param1='~/Documents/Organized'"
echo "Edit Config | bash='open' param1='-e' param2='$AGENT_PATH/config.yaml'"

# Check if running with parameter
if [ "$1" == "run" ]; then
    cd "$AGENT_PATH"
    source "$VENV_PATH/bin/activate"
    python3 main.py
    exit 0
elif [ "$1" == "dry-run" ]; then
    cd "$AGENT_PATH"
    source "$VENV_PATH/bin/activate"
    python3 main.py --dry-run
    exit 0
fi

# Show last run info
if [ -f "$LOG_FILE" ]; then
    LAST_RUN=$(tail -n 20 "$LOG_FILE" | grep "CLEANUP COMPLETE" | tail -n 1)
    if [ -n "$LAST_RUN" ]; then
        echo "---"
        echo "Last Run:"
        echo "$LAST_RUN | size=12"
    fi
fi
```

### 3. Make Script Executable

```bash
chmod +x ~/.swiftbar/cleanup-agent.1h.sh
```

### 4. Schedule Options

The filename determines the refresh interval:
- `cleanup-agent.1h.sh` - Runs every 1 hour
- `cleanup-agent.30m.sh` - Runs every 30 minutes
- `cleanup-agent.1d.sh` - Runs once per day
- `cleanup-agent.manual.sh` - Manual trigger only

### 5. Alternative: LaunchAgent (macOS Native Scheduling)

Create `~/Library/LaunchAgents/com.cleanup-agent.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cleanup-agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/simkeyur/src/local-agents/mac-cleanup-agent/venv/bin/python3</string>
        <string>/Users/simkeyur/src/local-agents/mac-cleanup-agent/main.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/simkeyur/src/local-agents/mac-cleanup-agent/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/simkeyur/src/local-agents/mac-cleanup-agent/launchd.error.log</string>
</dict>
</plist>
```

Load the agent:
```bash
launchctl load ~/Library/LaunchAgents/com.cleanup-agent.plist
```

## Logging

Logs are written to `cleanup_agent.log` in the project directory. Check the log to see:
- Which files were organized
- Where they were moved to
- Any errors or warnings
- AI classification results

### Log Retention

The agent automatically manages log files with a **rolling 7-day retention policy**:
- ✅ Logs older than 7 days are automatically deleted
- ✅ Each run cleans up old log files first
- ✅ Prevents disk space issues from log accumulation
- ✅ Configurable in `config.yaml` (`logging.retention_days`)

To change the retention period, edit `config.yaml`:
```yaml
logging:
  retention_days: 14  # Keep logs for 14 days instead
```

## Switching Ollama Models

To use a different Ollama model:

1. Pull the model:
```bash
ollama pull mistral
```

2. Update `config.yaml`:
```yaml
ollama:
  model: "mistral"
```

Popular models:
- `llama3.2` - Fast and efficient
- `mistral` - Great balance of speed and accuracy
- `llama3.1` - More powerful, slower
- `phi3` - Very lightweight

## Troubleshooting

### Ollama Connection Error

Make sure Ollama is running:
```bash
ollama serve
```

### Permission Errors

Grant terminal/Python full disk access in System Preferences → Security & Privacy → Privacy → Full Disk Access

### Files Not Moving

1. Check if dry-run mode is enabled in config
2. Verify folder paths in config are correct
3. Check logs for specific errors

## License

MIT License - feel free to modify and use as needed!
