# Obsidian Checker - Standalone GUI

This is the standalone version of the Obsidian Checker GUI that doesn't require shell scripts to run.

## Running the Standalone GUI

You have several options to launch the GUI:

### Option 1: Using the standalone launcher
```bash
python3 run_gui.py
```

### Option 2: Running the GUI directly
```bash
python3 obsidian_gui.py
```

### Option 3: Making it executable (macOS/Linux)
```bash
chmod +x run_gui.py
./run_gui.py
```

## Features

The standalone GUI includes all the core functionality:

- ✅ **Backlink Analysis**: Check for broken links in your Obsidian vault
- ✅ **Text Search**: Search across all markdown files
- ✅ **AI Search**: Semantic search using AI (if dependencies are installed)
- ✅ **Export Results**: Save analysis results to markdown files
- ✅ **Vault Auto-detection**: Automatically find Obsidian vaults
- ✅ **Cross-platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- pathlib (included with Python 3.4+)

### Optional AI Dependencies

For AI-powered semantic search:
- sentence-transformers
- sklearn
- numpy

Install with: `pip install sentence-transformers scikit-learn numpy`

## What Changed

This standalone version:
- ❌ **No longer requires** shell scripts (`launch_gui.sh`, `run_with_ai.sh`)
- ❌ **No longer calls** external CLI processes via subprocess
- ✅ **Includes all functionality** directly in the GUI code
- ✅ **Faster execution** (no process spawning overhead)
- ✅ **Simpler deployment** (single Python file)
- ✅ **Better error handling** (no shell script dependencies)

## Troubleshooting

If you encounter issues:

1. **Import errors**: Make sure all files are in the same directory
2. **AI features unavailable**: Install optional dependencies or disable AI features
3. **GUI won't start**: Check that tkinter is installed (`python3 -m tkinter`)

The GUI will gracefully fallback to standard text search if AI dependencies are not available.