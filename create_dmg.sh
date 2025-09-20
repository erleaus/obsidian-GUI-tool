#!/bin/bash

# Script to create DMG installer for Obsidian Checker

set -e

APP_NAME="Obsidian Checker"
DMG_NAME="ObsidianChecker-v1.0.0"
APP_PATH="dist/Obsidian Checker.app"
DMG_DIR="dmg_temp"
DMG_PATH="dist/${DMG_NAME}.dmg"

echo "🔨 Creating DMG installer for ${APP_NAME}..."

# Clean up any previous DMG build
if [ -d "${DMG_DIR}" ]; then
    echo "🧹 Cleaning up previous build..."
    rm -rf "${DMG_DIR}"
fi

if [ -f "${DMG_PATH}" ]; then
    echo "🗑️  Removing existing DMG..."
    rm -f "${DMG_PATH}"
fi

# Create temporary DMG directory
echo "📁 Creating temporary DMG directory..."
mkdir -p "${DMG_DIR}"

# Copy the app to DMG directory
echo "📋 Copying app to DMG directory..."
cp -R "${APP_PATH}" "${DMG_DIR}/"

# Create Applications shortcut
echo "🔗 Creating Applications shortcut..."
ln -sf /Applications "${DMG_DIR}/Applications"

# Create README for users
echo "📝 Creating README for users..."
cat > "${DMG_DIR}/README.txt" << 'EOF'
Obsidian Checker v1.0.0
========================

Installation Instructions:
1. Drag "Obsidian Checker.app" to the Applications folder
2. Launch from Launchpad or Applications folder
3. If macOS shows a security warning, go to System Preferences > Security & Privacy and click "Open Anyway"

Features:
- Backlink Analysis: Check for broken links in Obsidian vaults
- Text Search: Search across all markdown files
- AI Search: Semantic search using AI (optional)
- Export Results: Save analysis results to markdown files
- Vault Auto-detection: Automatically find Obsidian vaults

System Requirements:
- macOS 10.13 (High Sierra) or later
- No additional dependencies required

For support and updates:
https://github.com/your-username/obsidian-checker

© 2025 Eric Austin. All rights reserved.
EOF

# Create the DMG
echo "💿 Creating DMG file..."
hdiutil create -volname "${APP_NAME}" \
    -srcfolder "${DMG_DIR}" \
    -ov \
    -format UDZO \
    -imagekey zlib-level=9 \
    "${DMG_PATH}"

# Clean up temporary directory
echo "🧹 Cleaning up..."
rm -rf "${DMG_DIR}"

# Get file size for display
DMG_SIZE=$(du -h "${DMG_PATH}" | cut -f1)

echo "✅ DMG created successfully!"
echo "📄 File: ${DMG_PATH}"
echo "📏 Size: ${DMG_SIZE}"
echo ""
echo "🚀 Ready for distribution!"
echo "   Users can download and install by:"
echo "   1. Double-clicking the DMG file"
echo "   2. Dragging the app to Applications"
echo "   3. Launching from Applications or Launchpad"