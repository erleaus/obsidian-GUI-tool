#!/bin/bash
# Simple launcher for Obsidian Checker Desktop App
# Can be used from command line or added to PATH

echo "🚀 Launching Obsidian Checker Desktop App..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if the app exists
APP_PATH="$SCRIPT_DIR/Obsidian Checker.app"

if [ -d "$APP_PATH" ]; then
    echo "📱 Opening Obsidian Checker.app..."
    open "$APP_PATH"
else
    echo "❌ Desktop app not found. Creating it now..."
    if [ -x "$SCRIPT_DIR/create_desktop_app.sh" ]; then
        "$SCRIPT_DIR/create_desktop_app.sh"
        if [ -d "$APP_PATH" ]; then
            echo "✅ App created successfully! Opening..."
            open "$APP_PATH"
        else
            echo "❌ Failed to create app. Launching CLI version instead..."
            cd "$SCRIPT_DIR"
            python3 obsidian_backlink_checker.py
        fi
    else
        echo "❌ Cannot create app. Launching CLI version instead..."
        cd "$SCRIPT_DIR"
        python3 obsidian_backlink_checker.py
    fi
fi