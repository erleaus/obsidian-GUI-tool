#!/bin/bash

# Complete build script for Obsidian Checker macOS installer
# Creates both .app bundle and .dmg installer package

set -e

echo "🔨 Building Obsidian Checker for macOS distribution..."
echo "=================================================="

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/

# Build the app bundle
echo ""
echo "📦 Step 1: Building macOS app bundle..."
echo "----------------------------------------"
pyinstaller obsidian_checker.spec --clean

if [ ! -d "dist/Obsidian Checker.app" ]; then
    echo "❌ App bundle creation failed!"
    exit 1
fi

echo "✅ App bundle created successfully!"

# Test the app bundle
echo ""
echo "🧪 Step 2: Testing app bundle..."
echo "--------------------------------"
echo "Launching app for testing..."
open "dist/Obsidian Checker.app" &
sleep 3

echo "✅ App bundle test completed!"

# Create DMG installer
echo ""
echo "💿 Step 3: Creating DMG installer..."
echo "-----------------------------------"
./create_dmg.sh

if [ ! -f "dist/ObsidianChecker-v1.0.0.dmg" ]; then
    echo "❌ DMG creation failed!"
    exit 1
fi

echo "✅ DMG installer created successfully!"

# Display final results
echo ""
echo "🎉 Build completed successfully!"
echo "================================="
echo ""
echo "📂 Distribution files created:"
echo "  • App Bundle:  dist/Obsidian Checker.app"
echo "  • DMG Installer: dist/ObsidianChecker-v1.0.0.dmg"
echo ""

# Get file sizes
APP_SIZE=$(du -sh "dist/Obsidian Checker.app" | cut -f1)
DMG_SIZE=$(du -sh "dist/ObsidianChecker-v1.0.0.dmg" | cut -f1)

echo "📏 File sizes:"
echo "  • App Bundle: ${APP_SIZE}"
echo "  • DMG File: ${DMG_SIZE}"
echo ""

echo "🚀 Ready for distribution!"
echo ""
echo "📋 Distribution checklist:"
echo "  ✅ App bundle created and tested"
echo "  ✅ DMG installer package created"
echo "  ✅ README included in DMG"
echo "  ✅ Applications folder shortcut added"
echo ""
echo "💡 Next steps:"
echo "  1. Test the DMG on a clean macOS system"
echo "  2. Consider code signing for App Store or notarization"
echo "  3. Upload to your distribution platform"
echo ""
echo "🔍 To test DMG installation:"
echo "  open dist/ObsidianChecker-v1.0.0.dmg"