#!/usr/bin/env python3
"""
DMG Packaging Script for Obsidian Checker
Creates a standalone macOS application and packages it into a DMG file.
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path

# App configuration
APP_NAME = "Obsidian Checker"
APP_VERSION = "1.0.0"
APP_IDENTIFIER = "com.obsidian.checker"
MAIN_SCRIPT = "obsidian_backlink_checker.py"
DMG_NAME = f"{APP_NAME.replace(' ', '_')}_v{APP_VERSION}"

def check_dependencies():
    """Check if required tools are installed"""
    print("🔍 Checking dependencies...")
    
    required_tools = {
        'python': 'Python 3',
        'pip': 'pip package manager'
    }
    
    missing_tools = []
    for tool, description in required_tools.items():
        if shutil.which(tool) is None:
            missing_tools.append(f"{tool} ({description})")
    
    if missing_tools:
        print(f"❌ Missing required tools: {', '.join(missing_tools)}")
        return False
    
    # Check for PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller is available")
    except ImportError:
        print("⚠️ PyInstaller not found, will install it...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print("✅ PyInstaller installed")
    
    print("✅ All dependencies satisfied")
    return True

def create_app_icon():
    """Create a basic app icon (you can replace with a custom icon)"""
    icon_path = Path("resources/icon.icns")
    
    if icon_path.exists():
        print("✅ Using existing icon")
        return str(icon_path)
    
    print("ℹ️ No custom icon found, PyInstaller will use default")
    return None

def create_info_plist():
    """Create Info.plist content for the app bundle"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>{APP_NAME}</string>
    <key>CFBundleExecutable</key>
    <string>{APP_NAME.replace(' ', '_').lower()}</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundleIdentifier</key>
    <string>{APP_IDENTIFIER}</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>{APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>{APP_VERSION}</string>
    <key>CFBundleVersion</key>
    <string>{APP_VERSION}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2024. All rights reserved.</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>md</string>
            </array>
            <key>CFBundleTypeName</key>
            <string>Markdown Document</string>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
            <key>LSItemContentTypes</key>
            <array>
                <string>net.daringfireball.markdown</string>
            </array>
        </dict>
    </array>
</dict>
</plist>"""

def build_app():
    """Build the standalone application using PyInstaller"""
    print("🔨 Building standalone application...")
    
    # Prepare build directory
    build_dir = Path("build_dmg")
    build_dir.mkdir(exist_ok=True)
    
    # Create PyInstaller spec file
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('GUI_README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'numpy', 'PIL', 'tkinter.test'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME.replace(' ', '_').lower()}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME.replace(' ', '_').lower()}',
)

app = BUNDLE(
    coll,
    name='{APP_NAME}.app',
    icon=None,
    bundle_identifier='{APP_IDENTIFIER}',
    version='{APP_VERSION}',
    info_plist={{
        'CFBundleShortVersionString': '{APP_VERSION}',
        'CFBundleVersion': '{APP_VERSION}',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    }},
)
"""
    
    spec_file = build_dir / "app.spec"
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    # Run PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        str(spec_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
        if result.returncode != 0:
            print(f"❌ PyInstaller failed:")
            print(result.stderr)
            return False
        
        app_path = Path("dist") / f"{APP_NAME}.app"
        if app_path.exists():
            print(f"✅ Application built successfully: {app_path}")
            return str(app_path)
        else:
            print("❌ Application bundle not found after build")
            return False
            
    except Exception as e:
        print(f"❌ Error during build: {e}")
        return False

def create_dmg(app_path):
    """Create a DMG file from the application"""
    print("📦 Creating DMG file...")
    
    dmg_dir = Path("dmg_contents")
    dmg_dir.mkdir(exist_ok=True)
    
    # Copy app to DMG contents
    app_name = Path(app_path).name
    dmg_app_path = dmg_dir / app_name
    
    if dmg_app_path.exists():
        shutil.rmtree(dmg_app_path)
    
    shutil.copytree(app_path, dmg_app_path)
    print(f"✅ Copied {app_name} to DMG contents")
    
    # Create Applications symlink
    applications_link = dmg_dir / "Applications"
    if applications_link.exists():
        applications_link.unlink()
    applications_link.symlink_to("/Applications")
    print("✅ Created Applications symlink")
    
    # Add README to DMG
    readme_content = f"""# {APP_NAME} v{APP_VERSION}

## Installation
1. Drag "{APP_NAME}" to the Applications folder
2. Open Applications and launch "{APP_NAME}"

## About
{APP_NAME} is a tool for analyzing Obsidian vaults, checking backlinks, and searching content.

## Features
- Backlink analysis and broken link detection
- AI-powered semantic search (optional)
- Quick content search
- Export results to various formats

## System Requirements
- macOS 10.13 (High Sierra) or later
- Internet connection for AI features (optional)

## Support
For issues or questions, please visit the project repository.

---
Built with ❤️ for the Obsidian community
"""
    
    readme_file = dmg_dir / "README.txt"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    # Create DMG using hdiutil
    dmg_temp = f"{DMG_NAME}_temp.dmg"
    dmg_final = f"{DMG_NAME}.dmg"
    
    # Remove existing files
    for dmg_file in [dmg_temp, dmg_final]:
        if Path(dmg_file).exists():
            Path(dmg_file).unlink()
    
    try:
        # Create temporary DMG
        cmd_create = [
            'hdiutil', 'create', 
            '-srcfolder', str(dmg_dir),
            '-volname', f"{APP_NAME} v{APP_VERSION}",
            '-format', 'UDRW',  # Read-write for customization
            dmg_temp
        ]
        
        result = subprocess.run(cmd_create, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ DMG creation failed: {result.stderr}")
            return False
        
        print("✅ Temporary DMG created")
        
        # Mount DMG for customization
        mount_result = subprocess.run(
            ['hdiutil', 'attach', dmg_temp, '-readwrite', '-nobrowse'],
            capture_output=True, text=True
        )
        
        if mount_result.returncode != 0:
            print("⚠️ Could not mount DMG for customization, using basic version")
        else:
            # Extract mount point
            mount_point = None
            for line in mount_result.stdout.split('\n'):
                if '/Volumes/' in line:
                    mount_point = line.split('\t')[-1].strip()
                    break
            
            if mount_point:
                print(f"✅ DMG mounted at: {mount_point}")
                
                # Set custom view options (basic)
                try:
                    # Create .DS_Store equivalent commands
                    subprocess.run(['osascript', '-e', f'''
                        tell application "Finder"
                            tell disk "{APP_NAME} v{APP_VERSION}"
                                open
                                set current view of container window to icon view
                                set toolbar visible of container window to false
                                set statusbar visible of container window to false
                                set the bounds of container window to {{100, 100, 600, 400}}
                                set arrangement of icon view options of container window to not arranged
                                set icon size of icon view options of container window to 128
                                set background picture of icon view options of container window to file ".background:background.png"
                                make new alias file at container window to POSIX file "/Applications" with properties {{name:"Applications"}}
                                set position of item "{APP_NAME}" of container window to {{150, 200}}
                                set position of item "Applications" of container window to {{350, 200}}
                                close
                            end tell
                        end tell
                    '''], capture_output=True)
                    print("✅ DMG customization applied")
                except:
                    print("⚠️ Could not apply DMG customization")
                
                # Unmount
                subprocess.run(['hdiutil', 'detach', mount_point], capture_output=True)
                print("✅ DMG unmounted")
        
        # Convert to final compressed DMG
        cmd_convert = [
            'hdiutil', 'convert', dmg_temp,
            '-format', 'UDZO',  # Compressed
            '-o', dmg_final
        ]
        
        result = subprocess.run(cmd_convert, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ DMG conversion failed: {result.stderr}")
            return False
        
        # Clean up
        Path(dmg_temp).unlink()
        shutil.rmtree(dmg_dir)
        
        dmg_size = Path(dmg_final).stat().st_size / (1024 * 1024)  # MB
        print(f"✅ DMG created successfully: {dmg_final} ({dmg_size:.1f} MB)")
        return dmg_final
        
    except Exception as e:
        print(f"❌ Error creating DMG: {e}")
        return False

def cleanup_build_files():
    """Clean up build artifacts"""
    print("🧹 Cleaning up build files...")
    
    paths_to_clean = [
        "build", "dist", "build_dmg", "__pycache__",
        "*.spec", "*.pyc"
    ]
    
    for path_pattern in paths_to_clean:
        for path in Path(".").glob(path_pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    
    print("✅ Cleanup completed")

def main():
    """Main function to orchestrate the DMG creation process"""
    print(f"🚀 Creating DMG for {APP_NAME} v{APP_VERSION}")
    print("=" * 50)
    
    # Check if main script exists
    if not Path(MAIN_SCRIPT).exists():
        print(f"❌ Main script not found: {MAIN_SCRIPT}")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    try:
        # Build the application
        app_path = build_app()
        if not app_path:
            return 1
        
        # Create DMG
        dmg_path = create_dmg(app_path)
        if not dmg_path:
            return 1
        
        print("\n" + "=" * 50)
        print(f"🎉 SUCCESS! DMG created: {dmg_path}")
        print("\n📋 Next steps:")
        print(f"1. Test the DMG by opening: {dmg_path}")
        print(f"2. Drag '{APP_NAME}' to Applications")
        print(f"3. Launch from Applications folder")
        print("\n💡 Tips:")
        print("- The DMG includes installation instructions")
        print("- The app is self-contained and portable")
        print("- No additional dependencies required on target Mac")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Build cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    finally:
        # Always cleanup, even if there's an error
        cleanup_build_files()

if __name__ == "__main__":
    exit(main())