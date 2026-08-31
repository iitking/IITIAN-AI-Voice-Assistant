#!/bin/bash
# ----------------------------------------------------
# 🤖 IITIAN AI Voice Assistant - One-Click Launcher
# Double-click this file from Finder to run!
# ----------------------------------------------------

cd "$(dirname "$0")"

echo "=================================================="
echo "🤖 Starting IITIAN AI Assistant Server..."
echo "=================================================="

# Check for python3
if command -v /opt/homebrew/bin/python3.12 &>/dev/null; then
    PYTHON_CMD="/opt/homebrew/bin/python3.12"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Error: Python 3 not found!"
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD run.py
