#!/bin/bash
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.refreshOnOpen>true</swiftbar.refreshOnOpen>

# Metadata
# <swiftbar.title>Cleanup Agent</swiftbar.title>
# <swiftbar.version>v1.0</swiftbar.version>
# <swiftbar.author>Mac Cleanup Agent</swiftbar.author>
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
