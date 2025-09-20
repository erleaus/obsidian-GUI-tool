# 🖥️ Obsidian Checker - Cross-Platform GUI

A modern, user-friendly graphical interface for the Obsidian Checker tool that works on **Windows, macOS, and Linux**.

## ✨ Features

### 🎯 Core Functionality
- **Vault Detection**: Browse or auto-find Obsidian vaults
- **Backlink Analysis**: Check for broken links and references
- **AI-Powered Search**: Semantic analysis (when AI environment is set up)
- **Export Results**: Save analysis results to markdown files
- **Real-time Output**: Live display of analysis progress

### 🔧 User Interface
- **Modern Design**: Clean, responsive interface using Tkinter
- **Cross-Platform**: Native look and feel on each operating system
- **Progress Tracking**: Visual progress bars and status updates
- **Help System**: Built-in help and documentation
- **Error Handling**: User-friendly error messages and guidance

### 🤖 AI Integration
- **Automatic Detection**: Detects if AI environment is available
- **Smart Fallback**: Works with or without AI features
- **Status Indicators**: Clear visual indication of AI availability

## 🚀 How to Launch

### Option 1: GUI Launcher (Recommended)
```bash
./launch_gui.sh
```

### Option 2: Direct Python Launch
```bash
python3 obsidian_gui.py
```

### Option 3: Desktop Shortcut
Double-click `Launch Obsidian Checker.command` on your desktop

## 📋 Requirements

### Minimum Requirements
- **Python 3.8+** (with Tkinter support)
- **Operating System**: Windows 10+, macOS 10.14+, or Linux with GUI support

### For AI Features (Optional)
- Virtual environment: `obsidian_ai_env/`
- AI dependencies installed via `./setup.sh`

## 🎮 How to Use

1. **Launch the GUI** using one of the methods above
2. **Select Your Vault**:
   - Click "Browse..." to manually select your Obsidian vault folder
   - Click "Auto-find" to search common locations automatically
3. **Choose Analysis Options**:
   - ☑️ Check backlinks and broken links
   - ☑️ AI semantic search (if available)
   - ☑️ Export results to markdown file
4. **Run Analysis**: Click "🚀 Run Analysis"
5. **View Results**: Analysis output appears in real-time in the results area

## 📁 Interface Layout

```
┌─────────────────────────────────────────────┐
│ 🔗 Obsidian Checker                        │
├─────────────────────────────────────────────┤
│ 📁 Obsidian Vault                          │
│ Vault Path: [_______________] [Browse] [Auto] │
├─────────────────────────────────────────────┤
│ 🔧 Analysis Options                        │
│ ☑ Check backlinks and broken links         │
│ ☑ AI semantic search            ✅ AI Ready │
│ ☐ Export results to markdown               │
├─────────────────────────────────────────────┤
│ [🚀 Run] [⏹ Stop] [⚙️ Settings] [❓ Help]  │
├─────────────────────────────────────────────┤
│ 📊 Results                                  │
│ ┌─────────────────────────────────────────┐ │
│ │ Analysis output appears here...         │ │
│ │                                         │ │
│ └─────────────────────────────────────────┘ │
│ [Progress Bar]                              │
│ Status: Ready                               │
└─────────────────────────────────────────────┘
```

## 🔧 Features in Detail

### Auto-Find Vaults
The GUI can automatically search for Obsidian vaults in common locations:
- `~/Documents/`
- `~/Desktop/`
- `~/Obsidian/`
- `~/Documents/Obsidian/`
- `~/iCloud Drive (Archive)/Obsidian/` (macOS)

### AI Status Indicators
- ✅ **AI Ready**: AI environment detected and ready
- ⚠️ **AI Not Set Up**: AI environment not found (run `./setup.sh`)
- ❌ **AI Error**: Problem with AI configuration

### Threading & Performance
- **Non-blocking UI**: Analysis runs in background thread
- **Real-time Updates**: Live output streaming
- **Cancellable Operations**: Stop analysis at any time
- **Progress Feedback**: Visual progress indication

## 🐛 Troubleshooting

### GUI Won't Start
```bash
# Check Python and Tkinter
python3 -c "import tkinter; print('Tkinter OK')"

# If Tkinter is missing, install it:
# Ubuntu/Debian: sudo apt-get install python3-tk
# macOS: Should be included with Python
# Windows: Should be included with Python
```

### AI Features Not Available
```bash
# Set up AI environment
./setup.sh

# Or check if environment exists
ls -la obsidian_ai_env/
```

### Vault Not Detected
- Ensure the selected folder contains a `.obsidian` subfolder
- Check folder permissions
- Try browsing manually instead of auto-find

## 🔄 Updating

To get the latest GUI features:
```bash
git pull origin desktop-launcher-testing
```

## 📝 Feedback & Development

This GUI is part of the `desktop-launcher-testing` branch. Features and improvements are actively being developed.

### Current Status: ✅ Working
- Cross-platform compatibility
- AI integration
- Real-time analysis output
- Export functionality

### Planned Improvements:
- Enhanced settings dialog
- Analysis result filtering
- Custom export formats
- Performance optimizations