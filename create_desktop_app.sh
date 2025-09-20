#!/bin/bash
# Create macOS Desktop App for Obsidian Checker
# This script creates an .app bundle that can be launched from Finder

echo "🖥️  Creating macOS Desktop App for Obsidian Checker..."
echo "======================================================"

# Get the current directory (should be the project root)
PROJECT_DIR="$(pwd)"
echo "📁 Project directory: $PROJECT_DIR"

# Create the app bundle structure
APP_NAME="Obsidian Checker"
APP_DIR="$PROJECT_DIR/$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

echo "🏗️  Creating app bundle structure..."
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create Info.plist
echo "📄 Creating Info.plist..."
cat > "$CONTENTS_DIR/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleExecutable</key>
    <string>launch_obsidian_checker</string>
    <key>CFBundleIconFile</key>
    <string>app_icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.ericaustin.obsidian-checker</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Obsidian Checker</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>CFBundleDisplayName</key>
    <string>Obsidian Checker</string>
    <key>CFBundleGetInfoString</key>
    <string>AI-Enhanced Obsidian Vault Analysis Tool</string>
</dict>
</plist>
EOF

# Create the main executable script
echo "🚀 Creating launcher script..."
cat > "$MACOS_DIR/launch_obsidian_checker" << EOF
#!/bin/bash
# Obsidian Checker Desktop App Launcher

# Get the directory where the app is located
APP_DIR="\$(dirname "\$0")/../.."
PROJECT_DIR="\$(dirname "\$APP_DIR")"

# Change to the project directory
cd "\$PROJECT_DIR"

# Check if AI environment exists
if [ -d "obsidian_ai_env" ]; then
    echo "🤖 Launching with AI features..."
    ./run_with_ai.sh obsidian_backlink_checker.py
else
    # Try to set up AI environment
    if command -v python3 &> /dev/null; then
        osascript -e 'display dialog "AI features not set up. Would you like to install them now? This will take a few minutes." buttons {"Cancel", "Install AI Features"} default button "Install AI Features"' 2>/dev/null
        
        if [ \$? -eq 0 ]; then
            # User chose to install
            osascript -e 'display notification "Installing AI dependencies..." with title "Obsidian Checker"'
            ./setup.sh
            
            if [ -d "obsidian_ai_env" ]; then
                osascript -e 'display notification "AI setup complete! Launching with AI features." with title "Obsidian Checker"'
                ./run_with_ai.sh obsidian_backlink_checker.py
            else
                osascript -e 'display notification "AI setup failed. Launching without AI features." with title "Obsidian Checker"'
                python3 obsidian_backlink_checker.py
            fi
        else
            # User cancelled, launch without AI
            python3 obsidian_backlink_checker.py
        fi
    else
        osascript -e 'display dialog "Python 3 is required but not found. Please install Python 3.8 or later." buttons {"OK"} default button "OK"'
    fi
fi
EOF

# Make the launcher executable
chmod +x "$MACOS_DIR/launch_obsidian_checker"

# Create a simple icon (we'll use a colored square for now)
echo "🎨 Creating app icon..."

# Use Python to create a simple icon
python3 << 'PYTHON_SCRIPT'
try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Create a 512x512 icon
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create a rounded rectangle background
    margin = 50
    corner_radius = 80
    
    # Background gradient-like effect
    for i in range(10):
        alpha = 255 - (i * 20)
        color = (45 + i*5, 156 + i*3, 219 - i*5, alpha)
        offset = i * 3
        draw.rounded_rectangle(
            [margin + offset, margin + offset, size - margin - offset, size - margin - offset],
            radius=corner_radius - offset,
            fill=color
        )
    
    # Add main icon elements
    # Draw a magnifying glass
    center_x, center_y = size // 2, size // 2 - 30
    glass_radius = 60
    handle_length = 40
    
    # Glass circle
    draw.ellipse([center_x - glass_radius, center_y - glass_radius, 
                  center_x + glass_radius, center_y + glass_radius], 
                 outline=(255, 255, 255, 255), width=12)
    
    # Glass handle
    handle_start_x = center_x + glass_radius - 15
    handle_start_y = center_y + glass_radius - 15
    handle_end_x = handle_start_x + handle_length
    handle_end_y = handle_start_y + handle_length
    
    draw.line([handle_start_x, handle_start_y, handle_end_x, handle_end_y], 
              fill=(255, 255, 255, 255), width=12)
    
    # Add AI sparkles
    sparkle_positions = [
        (center_x - 80, center_y - 80),
        (center_x + 80, center_y - 90),
        (center_x - 70, center_y + 70),
        (center_x + 90, center_y + 60)
    ]
    
    for pos in sparkle_positions:
        # Draw a small star/sparkle
        draw.polygon([
            (pos[0], pos[1] - 10),      # top
            (pos[0] + 3, pos[1] - 3),   # top right
            (pos[0] + 10, pos[1]),      # right
            (pos[0] + 3, pos[1] + 3),   # bottom right
            (pos[0], pos[1] + 10),      # bottom
            (pos[0] - 3, pos[1] + 3),   # bottom left
            (pos[0] - 10, pos[1]),      # left
            (pos[0] - 3, pos[1] - 3)    # top left
        ], fill=(255, 215, 0, 255))
    
    # Save as PNG first
    resources_dir = os.environ.get('RESOURCES_DIR', '.')
    png_path = os.path.join(resources_dir, 'app_icon.png')
    img.save(png_path, 'PNG')
    print(f"✅ Created icon at: {png_path}")
    
    # Try to convert to icns format if possible
    icns_path = os.path.join(resources_dir, 'app_icon.icns')
    try:
        # Use sips command on macOS to convert PNG to ICNS
        import subprocess
        result = subprocess.run(['sips', '-s', 'format', 'icns', png_path, '--out', icns_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created ICNS icon at: {icns_path}")
            # Remove the PNG file
            os.remove(png_path)
        else:
            print(f"⚠️  Could not create ICNS, keeping PNG: {png_path}")
    except:
        print(f"⚠️  Could not create ICNS, keeping PNG: {png_path}")
    
except ImportError:
    print("⚠️  PIL not available, creating simple text icon...")
    # Create a simple text file as fallback
    resources_dir = os.environ.get('RESOURCES_DIR', '.')
    icon_path = os.path.join(resources_dir, 'app_icon.txt')
    with open(icon_path, 'w') as f:
        f.write("🤖🔍 Obsidian Checker")
    print(f"✅ Created simple icon placeholder at: {icon_path}")
PYTHON_SCRIPT

# Export the RESOURCES_DIR for Python script
export RESOURCES_DIR="$RESOURCES_DIR"

# Run the Python script to create the icon
python3 << 'EOF'
import os
try:
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a 512x512 icon
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create a rounded rectangle background
    margin = 50
    corner_radius = 80
    
    # Background gradient-like effect
    for i in range(10):
        alpha = 255 - (i * 20)
        color = (45 + i*5, 156 + i*3, 219 - i*5, alpha)
        offset = i * 3
        draw.rounded_rectangle(
            [margin + offset, margin + offset, size - margin - offset, size - margin - offset],
            radius=corner_radius - offset,
            fill=color
        )
    
    # Add main icon elements
    # Draw a magnifying glass
    center_x, center_y = size // 2, size // 2 - 30
    glass_radius = 60
    handle_length = 40
    
    # Glass circle
    draw.ellipse([center_x - glass_radius, center_y - glass_radius, 
                  center_x + glass_radius, center_y + glass_radius], 
                 outline=(255, 255, 255, 255), width=12)
    
    # Glass handle
    handle_start_x = center_x + glass_radius - 15
    handle_start_y = center_y + glass_radius - 15
    handle_end_x = handle_start_x + handle_length
    handle_end_y = handle_start_y + handle_length
    
    draw.line([handle_start_x, handle_start_y, handle_end_x, handle_end_y], 
              fill=(255, 255, 255, 255), width=12)
    
    # Add AI sparkles
    sparkle_positions = [
        (center_x - 80, center_y - 80),
        (center_x + 80, center_y - 90),
        (center_x - 70, center_y + 70),
        (center_x + 90, center_y + 60)
    ]
    
    for pos in sparkle_positions:
        # Draw a small star/sparkle
        draw.polygon([
            (pos[0], pos[1] - 10),      # top
            (pos[0] + 3, pos[1] - 3),   # top right
            (pos[0] + 10, pos[1]),      # right
            (pos[0] + 3, pos[1] + 3),   # bottom right
            (pos[0], pos[1] + 10),      # bottom
            (pos[0] - 3, pos[1] + 3),   # bottom left
            (pos[0] - 10, pos[1]),      # left
            (pos[0] - 3, pos[1] - 3)    # top left
        ], fill=(255, 215, 0, 255))
    
    # Save as PNG first
    resources_dir = os.environ.get('RESOURCES_DIR', '.')
    png_path = os.path.join(resources_dir, 'app_icon.png')
    img.save(png_path, 'PNG')
    print(f"✅ Created icon at: {png_path}")
    
    # Try to convert to icns format if possible
    icns_path = os.path.join(resources_dir, 'app_icon.icns')
    try:
        # Use sips command on macOS to convert PNG to ICNS
        import subprocess
        result = subprocess.run(['sips', '-s', 'format', 'icns', png_path, '--out', icns_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Created ICNS icon at: {icns_path}")
            # Remove the PNG file
            os.remove(png_path)
        else:
            print(f"⚠️  Could not create ICNS, keeping PNG: {png_path}")
    except:
        print(f"⚠️  Could not create ICNS, keeping PNG: {png_path}")
    
except ImportError:
    print("⚠️  PIL not available, creating simple emoji icon...")
    # Create a simple text-based icon using macOS textutil
    resources_dir = os.environ.get('RESOURCES_DIR', '.')
    
    # Create a simple PNG using built-in macOS tools
    import subprocess
    import tempfile
    
    # Create a temporary AppleScript to generate an icon
    applescript = '''
    tell application "Image Events"
        launch
        set myImage to make new image with properties {dimensions:{512, 512}, color:{0, 0, 0, 0}}
        save myImage in POSIX file "{}/app_icon.png" as PNG
    end tell
    '''.format(resources_dir)
    
    try:
        result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
        if result.returncode != 0:
            # Fallback: create a simple file
            with open(os.path.join(resources_dir, 'app_icon.txt'), 'w') as f:
                f.write("🤖🔍 Obsidian Checker Icon")
            print("✅ Created simple icon placeholder")
    except:
        # Final fallback
        with open(os.path.join(resources_dir, 'app_icon.txt'), 'w') as f:
            f.write("🤖🔍 Obsidian Checker Icon")
        print("✅ Created simple icon placeholder")
EOF

echo ""
echo "🎉 Desktop app created successfully!"
echo ""
echo "📍 App location: $APP_DIR"
echo ""
echo "🚀 To use the app:"
echo "   1. Double-click 'Obsidian Checker.app' in Finder"
echo "   2. Or drag it to your Applications folder"
echo "   3. Or drag it to your Dock for quick access"
echo ""
echo "✨ The app will:"
echo "   - Auto-detect if AI features are available"
echo "   - Offer to install AI dependencies if needed"
echo "   - Launch the GUI with the best available features"
echo ""
echo "======================================================"