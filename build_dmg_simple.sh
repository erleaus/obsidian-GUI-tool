#!/bin/bash
# Simple DMG Build Script for Obsidian Checker
# Alternative approach using py2app

set -e  # Exit on any error

APP_NAME="Obsidian Checker"
APP_VERSION="1.0.0"
DMG_NAME="Obsidian_Checker_v${APP_VERSION}"
MAIN_SCRIPT="obsidian_backlink_checker.py"

echo "🚀 Building DMG for ${APP_NAME} v${APP_VERSION}"
echo "=================================================="

# Check if main script exists
if [[ ! -f "$MAIN_SCRIPT" ]]; then
    echo "❌ Main script not found: $MAIN_SCRIPT"
    exit 1
fi

# Create virtual environment for clean build
echo "🔧 Setting up build environment..."
if [[ -d "dmg_build_env" ]]; then
    rm -rf dmg_build_env
fi

python3 -m venv dmg_build_env
source dmg_build_env/bin/activate

# Install required packages
echo "📦 Installing build dependencies..."
pip install --upgrade pip
pip install pyinstaller

# Install app dependencies (minimal set)
if [[ -f "requirements.txt" ]]; then
    # Install only basic dependencies, skip heavy ML ones
    pip install sentence-transformers numpy scikit-learn || echo "⚠️ AI dependencies skipped"
fi

echo "🔨 Building standalone application..."

# Create PyInstaller command
pyinstaller \
    --name="$APP_NAME" \
    --windowed \
    --onedir \
    --clean \
    --noconfirm \
    --exclude-module=matplotlib \
    --exclude-module=scipy \
    --exclude-module=pandas \
    --exclude-module=PIL \
    --exclude-module=tkinter.test \
    --add-data="README.md:." \
    --add-data="GUI_README.md:." \
    "$MAIN_SCRIPT"

if [[ ! -d "dist/$APP_NAME.app" ]]; then
    echo "❌ Application build failed"
    exit 1
fi

echo "✅ Application built successfully"

# Create DMG contents directory
echo "📦 Creating DMG contents..."
DMG_DIR="dmg_contents"
if [[ -d "$DMG_DIR" ]]; then
    rm -rf "$DMG_DIR"
fi
mkdir "$DMG_DIR"

# Copy app to DMG contents
cp -R "dist/$APP_NAME.app" "$DMG_DIR/"

# Create Applications symlink
ln -s /Applications "$DMG_DIR/Applications"

# Create simple README
cat > "$DMG_DIR/README.txt" << EOF
# $APP_NAME v$APP_VERSION

## Installation Instructions
1. Drag "$APP_NAME" to the Applications folder
2. Open Applications and launch "$APP_NAME"

## About
$APP_NAME is a tool for analyzing Obsidian vaults:
- Check backlinks and find broken links  
- Search content across your vault
- AI-powered semantic search (optional)
- Export results in multiple formats

## System Requirements
- macOS 10.13 (High Sierra) or later
- Internet connection for AI features (optional)

## Getting Started
1. Launch the application
2. Browse to select your Obsidian vault folder
3. Choose analysis options
4. Click "Run Analysis" or use Quick Search

## Support
For issues or questions, please visit the project repository.

---
Built with ❤️ for the Obsidian community
EOF

# Create DMG
echo "📀 Creating DMG file..."
DMG_TEMP="${DMG_NAME}_temp.dmg"
DMG_FINAL="${DMG_NAME}.dmg"

# Remove existing DMG files
rm -f "$DMG_TEMP" "$DMG_FINAL"

# Create temporary DMG
hdiutil create -srcfolder "$DMG_DIR" -volname "$APP_NAME v$APP_VERSION" -format UDRW "$DMG_TEMP"

echo "✅ Temporary DMG created"

# Convert to compressed final DMG
hdiutil convert "$DMG_TEMP" -format UDZO -o "$DMG_FINAL"

# Get file size
DMG_SIZE=$(du -h "$DMG_FINAL" | cut -f1)

echo "✅ DMG created successfully: $DMG_FINAL ($DMG_SIZE)"

# Cleanup
echo "🧹 Cleaning up..."
rm -f "$DMG_TEMP"
rm -rf "$DMG_DIR"
rm -rf build dist *.spec
deactivate
rm -rf dmg_build_env

echo ""
echo "=================================================="
echo "🎉 SUCCESS! DMG Package Ready"
echo "=================================================="
echo "📁 File: $DMG_FINAL"
echo "💾 Size: $DMG_SIZE"
echo ""
echo "📋 Next Steps:"
echo "1. Test: open '$DMG_FINAL'"
echo "2. Verify: drag app to Applications"  
echo "3. Launch: from Applications folder"
echo ""
echo "💡 Distribution Tips:"
echo "- DMG contains installation instructions"
echo "- App is self-contained (no dependencies needed)"
echo "- Compatible with macOS 10.13+"
echo ""