#!/usr/bin/env python3
"""
Standalone Obsidian Checker GUI Launcher
Runs the GUI directly without shell script dependencies
"""

import sys
import os
from pathlib import Path

def main():
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Add current directory to Python path
    sys.path.insert(0, str(script_dir))
    
    print("🖥️  Launching Obsidian Checker GUI (Standalone)...")
    print("🚀 Starting GUI application...")
    
    try:
        # Import and run the GUI
        from obsidian_gui import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure obsidian_gui.py is in the same directory")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Application interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()