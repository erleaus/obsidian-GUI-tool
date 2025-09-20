# 📦 DMG Build Guide for Obsidian Checker

This guide explains how to create a distributable DMG (Disk Image) package for the Obsidian Checker application on macOS.

## 🎯 Overview

We provide two methods for building DMG packages:

1. **Python Script** (`create_dmg.py`) - Full-featured with customization
2. **Shell Script** (`build_dmg_simple.sh`) - Simple and reliable

Both create a standalone macOS application that can be distributed and installed without Python dependencies.

## 🔧 Prerequisites

### Required Tools
- **macOS 10.13+** (for building and target compatibility)
- **Python 3.8+** with pip
- **Xcode Command Line Tools** (for hdiutil and other system tools)

### Install Command Line Tools
```bash
xcode-select --install
```

## 🚀 Quick Start (Recommended)

### Option 1: Simple Shell Script

The easiest way to build a DMG:

```bash
# Make sure you're in the project directory
cd /path/to/obsidian-GUI-tool

# Run the build script
./build_dmg_simple.sh
```

This will:
1. ✅ Create a clean build environment
2. ✅ Install PyInstaller automatically
3. ✅ Build the standalone app
4. ✅ Package into DMG with installer interface
5. ✅ Clean up build artifacts

**Output**: `Obsidian_Checker_v1.0.0.dmg`

### Option 2: Python Script

For more control and customization:

```bash
# Install PyInstaller first (if not already installed)
pip install pyinstaller

# Run the Python build script
python create_dmg.py
```

## 📁 What Gets Created

### App Bundle Structure
```
Obsidian Checker.app/
├── Contents/
│   ├── Info.plist          # App metadata
│   ├── MacOS/
│   │   └── obsidian_checker # Main executable
│   ├── Resources/          # App resources
│   └── Frameworks/         # Python runtime & dependencies
```

### DMG Contents
```
Obsidian Checker v1.0.0/
├── Obsidian Checker.app    # The main application
├── Applications@           # Symlink to /Applications
└── README.txt             # Installation instructions
```

## 🔍 Build Process Details

### Step 1: Environment Setup
- Creates isolated build environment
- Installs PyInstaller and minimal dependencies
- Excludes heavy libraries (matplotlib, scipy) for smaller size

### Step 2: Application Building
```bash
pyinstaller \
    --name="Obsidian Checker" \
    --windowed \
    --onedir \
    --clean \
    --exclude-module=matplotlib \
    --add-data="README.md:." \
    obsidian_backlink_checker.py
```

### Step 3: DMG Creation
- Uses macOS `hdiutil` to create disk image
- Sets up drag-to-Applications interface
- Compresses for distribution
- Includes installation instructions

## 📊 File Sizes (Approximate)

| Component | Size | Notes |
|-----------|------|-------|
| App Bundle | ~150-200MB | Includes Python runtime |
| Compressed DMG | ~50-80MB | Final distribution file |
| Uncompressed | ~200MB | When mounted |

## 🛠️ Customization Options

### Custom App Icon
1. Create `resources/icon.icns` file
2. The build script will automatically use it
3. Use tools like Image2icon or online converters

### App Information
Edit these variables in the build scripts:
```bash
APP_NAME="Obsidian Checker"
APP_VERSION="1.0.0"
APP_IDENTIFIER="com.obsidian.checker"
```

### Included Files
Add additional files to be bundled:
```bash
--add-data="path/to/file:destination"
```

## 🐛 Troubleshooting

### Common Issues

**❌ "PyInstaller not found"**
```bash
pip install pyinstaller
```

**❌ "hdiutil command not found"**
```bash
xcode-select --install
```

**❌ "Permission denied"**
```bash
chmod +x build_dmg_simple.sh
```

**❌ Large file size**
- Build excludes heavy ML libraries by default
- For smaller size, remove AI search features
- Use `--exclude-module` for additional libraries

### Build Errors

**Import Errors During Build**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or build without AI features
pip install sentence-transformers numpy scikit-learn
```

**DMG Creation Fails**
```bash
# Ensure no existing DMG files
rm -f *.dmg

# Check disk space
df -h .
```

## 🧪 Testing Your DMG

### Verification Steps
1. **Open the DMG**: `open Obsidian_Checker_v1.0.0.dmg`
2. **Drag to Applications**: Test the install interface
3. **Launch from Applications**: Verify it runs correctly
4. **Test core features**: Open vault, run analysis
5. **Test on clean Mac**: Ensure no dependencies required

### Test Checklist
- [ ] DMG mounts correctly
- [ ] Drag-to-Applications works
- [ ] App launches from Applications
- [ ] Can select Obsidian vault
- [ ] Basic search works
- [ ] Backlink checking works
- [ ] Export functionality works
- [ ] No Python errors in Console.app

## 📤 Distribution

### For Public Release
1. **Code signing** (requires Apple Developer account):
   ```bash
   codesign --deep --force --verify --verbose --sign "Developer ID" "Obsidian Checker.app"
   ```

2. **Notarization** (for Gatekeeper approval):
   ```bash
   xcrun altool --notarize-app --file "Obsidian_Checker_v1.0.0.dmg"
   ```

### For Personal/Team Use
- DMG is ready to distribute as-is
- Users may need to right-click → "Open" for first launch
- Consider adding instructions about System Preferences → Security

## 🔄 Automated Builds

### GitHub Actions Example
```yaml
name: Build DMG
on: [push, pull_request]
jobs:
  build:
    runs-on: macos-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Build DMG
      run: ./build_dmg_simple.sh
    - name: Upload DMG
      uses: actions/upload-artifact@v3
      with:
        name: obsidian-checker-dmg
        path: "*.dmg"
```

## 📋 Build Script Options

### Environment Variables
```bash
# Customize before building
export APP_NAME="My Custom Name"
export APP_VERSION="2.0.0"
export DMG_NAME="My_Custom_DMG"

# Then build
./build_dmg_simple.sh
```

### Debug Mode
```bash
# Keep build files for inspection
export DEBUG_BUILD=1
./build_dmg_simple.sh
```

## 🎉 Success!

After successful build, you should see:
```
🎉 SUCCESS! DMG Package Ready
==================================================
📁 File: Obsidian_Checker_v1.0.0.dmg
💾 Size: 67M

📋 Next Steps:
1. Test: open 'Obsidian_Checker_v1.0.0.dmg'
2. Verify: drag app to Applications
3. Launch: from Applications folder
```

Your DMG is ready for distribution! 🚀

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all prerequisites are installed
3. Try the alternative build method
4. Check the Console.app for detailed error messages

---

*Happy packaging! 📦*