#!/bin/bash
# Launch the Obsidian Checker GUI
# Cross-platform Python GUI launcher

echo "🖥️  Launching Obsidian Checker GUI..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found."
    echo "   Please install Python 3.8 or later"
    exit 1
fi

# Launch the GUI
echo "🚀 Starting GUI application..."
python3 obsidian_gui.py