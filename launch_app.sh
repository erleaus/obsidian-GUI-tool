#!/bin/bash
# Obsidian Checker Launcher Script
# Launch the Obsidian Checker with AI features

echo "🚀 Launching Obsidian Checker..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if AI environment is set up
if [ -d "obsidian_ai_env" ] && [ -f "run_with_ai.sh" ]; then
    echo "🤖 Starting Obsidian Checker with AI features..."
    ./run_with_ai.sh obsidian_backlink_checker.py
else
    echo "⚠️  AI environment not found. Running setup..."
    if [ -f "setup.sh" ]; then
        ./setup.sh
        if [ -d "obsidian_ai_env" ]; then
            echo "✅ Setup complete! Starting with AI features..."
            ./run_with_ai.sh obsidian_backlink_checker.py
        else
            echo "❌ Setup failed. Running without AI features..."
            python3 obsidian_backlink_checker.py
        fi
    else
        echo "❌ Setup script not found. Running without AI features..."
        python3 obsidian_backlink_checker.py
    fi
fi
