# Obsidian Checker - macOS Packaging Guide

This guide explains how to build and distribute the Obsidian Checker as a macOS application.

## 🚀 Quick Start

To build both the app bundle and DMG installer:

```bash
./build_installer.sh
```

## 📦 What Gets Created

### 1. macOS App Bundle
- **File**: `dist/Obsidian Checker.app`
- **Size**: ~200MB (includes all Python dependencies)
- **Distribution**: Can be distributed directly or via DMG

### 2. DMG Installer Package
- **File**: `dist/ObsidianChecker-v1.0.0.dmg`
- **Size**: ~198MB (compressed)
- **Contents**: 
  - Obsidian Checker.app
  - Applications folder shortcut
  - README.txt with installation instructions

## 🛠️ Manual Build Process

### Step 1: Install Dependencies
```bash
pip3 install pyinstaller
```

### Step 2: Build App Bundle
```bash
pyinstaller obsidian_checker.spec --clean
```

### Step 3: Create DMG Installer
```bash
./create_dmg.sh
```

## 📋 Files Involved

### Core Build Files
- `obsidian_checker.spec` - PyInstaller configuration
- `create_dmg.sh` - DMG creation script
- `build_installer.sh` - Complete build automation

### Source Files
- `obsidian_gui.py` - Main application
- `obsidian_ai_search.py` - AI search functionality (optional)
- `STANDALONE_README.md` - Documentation

## 🔧 Customization Options

### App Bundle Settings
Edit `obsidian_checker.spec` to modify:
- App name and version
- Bundle identifier
- Icon (add `.icns` file)
- Additional data files
- Python dependencies

### DMG Settings
Edit `create_dmg.sh` to modify:
- DMG name and version
- Volume name
- Compression settings
- Additional files

## 🎯 Distribution Options

### Option 1: Direct App Distribution
- Share the `.app` bundle directly
- Users drag to Applications folder manually
- Smaller download (no DMG overhead)

### Option 2: DMG Installer (Recommended)
- Professional installation experience
- Includes helpful README and shortcuts
- Industry standard for macOS apps

### Option 3: Code Signing & Notarization
For wider distribution:
```bash
# Sign the app (requires Apple Developer account)
codesign --force --deep --sign "Developer ID Application: Your Name" "dist/Obsidian Checker.app"

# Create signed DMG
# (Additional steps required for notarization)
```

## 🧪 Testing

### Local Testing
```bash
# Test app bundle directly
open "dist/Obsidian Checker.app"

# Test DMG installation
open "dist/ObsidianChecker-v1.0.0.dmg"
```

### Clean System Testing
Test on a Mac without Python/development tools:
1. Mount the DMG
2. Drag app to Applications
3. Launch from Launchpad
4. Verify all features work

## 📊 Build Statistics

- **Build Time**: ~2-3 minutes
- **App Size**: ~200MB (includes PyTorch, scikit-learn, etc.)
- **DMG Size**: ~198MB (compressed)
- **Python Version**: 3.13
- **Dependencies**: All bundled (no external requirements)

## 🔍 Troubleshooting

### Common Issues

1. **PyInstaller not found**
   ```bash
   pip3 install pyinstaller
   ```

2. **Permission denied on scripts**
   ```bash
   chmod +x build_installer.sh create_dmg.sh
   ```

3. **App won't launch (Security)**
   - System Preferences > Security & Privacy
   - Click "Open Anyway" for the app

4. **Missing dependencies in app**
   - Add to `hiddenimports` in `obsidian_checker.spec`
   - Rebuild with `--clean` flag

### Build Logs
Check build logs for issues:
- PyInstaller warnings: `build/obsidian_checker/warn-obsidian_checker.txt`
- Console output during build process

## 🚀 Advanced Features

### Adding an Icon
1. Create `icon.icns` file
2. Update `obsidian_checker.spec`:
   ```python
   icon='icon.icns'
   ```

### Code Signing
1. Get Apple Developer certificate
2. Update build script with signing commands
3. Consider notarization for Gatekeeper compatibility

### Automated Builds
Integration with CI/CD:
- GitHub Actions for automated builds
- Version number automation
- Release asset uploads

## 📈 Next Steps

1. **Test thoroughly** on different macOS versions
2. **Consider code signing** for professional distribution
3. **Set up update mechanism** for future releases
4. **Create documentation** for end users
5. **Plan distribution strategy** (website, GitHub releases, etc.)

## 💡 Tips

- The app includes all Python dependencies (no user installation required)
- AI features work if dependencies are available during build
- The app gracefully handles missing AI dependencies
- DMG provides the best user experience for installation
- Consider creating both Intel and Apple Silicon builds for maximum compatibility