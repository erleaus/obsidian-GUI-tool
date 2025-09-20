#!/bin/bash
# Obsidian Checker Setup Script
# Sets up AI-powered Obsidian vault analysis tool

echo "🔧 Setting up Obsidian Checker with AI capabilities..."
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found."
    echo "   Please install Python 3.8 or later"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment for AI dependencies
echo "🐍 Creating virtual environment..."
python3 -m venv obsidian_ai_env

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    echo "   Make sure you have python3-venv installed"
    exit 1
fi

echo "✅ Virtual environment created"

# Activate virtual environment and install AI dependencies
echo "📦 Installing AI dependencies..."
source obsidian_ai_env/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Install AI dependencies
pip install sentence-transformers numpy scikit-learn

if [ $? -ne 0 ]; then
    echo "⚠️  AI dependencies installation failed"
    echo "   You can still use the tool without AI features"
    echo "   Run: python3 obsidian_backlink_checker.py"
else
    echo "✅ AI dependencies installed successfully!"
fi

deactivate

# Make scripts executable
chmod +x run_with_ai.sh
echo "✅ Scripts made executable"

echo ""
echo "🎉 Setup complete! Here's how to use your Obsidian Checker:"
echo ""
echo "📱 GUI with AI:"
echo "   ./run_with_ai.sh obsidian_backlink_checker.py"
echo ""
echo "💻 CLI with AI:"
echo "   ./run_with_ai.sh obsidian_checker_cli.py --help"
echo ""
echo "🎮 Interactive Menu:"
echo "   ./run_with_ai.sh obsidian_menu.py"
echo ""
echo "🔍 Without AI (original features):"
echo "   python3 obsidian_backlink_checker.py"
echo "   python3 obsidian_checker_cli.py --help"
echo "   python3 obsidian_menu.py"
echo ""
echo "📚 Read README.md for detailed usage instructions"
echo "=================================================="