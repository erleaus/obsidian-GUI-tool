# 🤖 AI-Enhanced Obsidian Checker

Your Obsidian Checker now includes **FREE AI-powered semantic search** capabilities! This enables conceptual search that goes beyond simple keyword matching.

## 🚀 Quick Start

### Run with AI Features:
```bash
# GUI with AI
./run_with_ai.sh obsidian_backlink_checker.py

# CLI with AI
./run_with_ai.sh obsidian_checker_cli.py --help

# Interactive Menu with AI
./run_with_ai.sh obsidian_menu.py
```

### Run without AI (original version):
```bash
# GUI without AI (shows AI info message)
python3 obsidian_backlink_checker.py

# CLI without AI (no AI options)
python3 obsidian_checker_cli.py --help
```

## 🧠 AI Features

### 1. **Concept Search**
Find notes by concept, not just exact keywords:
```bash
./run_with_ai.sh obsidian_checker_cli.py --ai-search "productivity techniques"
```

**Example Results:**
- Finds notes about GTD, time blocking, Pomodoro technique
- Discovers related concepts like focus, efficiency, workflow
- Returns similarity scores (30-100%)

### 2. **Similar File Discovery**
Find files conceptually similar to a given file:
```bash
./run_with_ai.sh obsidian_checker_cli.py --similar-to "notes/meditation.md"
```

**Example Results:**
- Finds notes about mindfulness, breathing exercises, wellness
- Discovers connected themes across your vault
- Perfect for finding related reading

### 3. **AI Index Management**
Build semantic search index (one-time setup per vault):
```bash
./run_with_ai.sh obsidian_checker_cli.py --build-ai-index
```

## 🎯 How AI Search Works

### Local AI Model
- Uses **sentence-transformers** with `all-MiniLM-L6-v2` model
- Runs **completely offline** - no data sent to external services
- **Free forever** - no API costs

### Intelligence Features
- **Semantic Understanding**: Understands concepts, not just words
- **Context Aware**: Considers meaning and relationships
- **Cached Results**: Fast subsequent searches (index cached in `.obsidian/`)
- **Progress Tracking**: Shows indexing progress for large vaults

## 🖥️ GUI Features

When running with AI, the GUI includes:

### 🤖 AI Concept Search Section
- **Concept field**: Enter conceptual queries
- **🤖 AI Concept Search**: Perform semantic search
- **🔄 Build AI Index**: Create/rebuild semantic index
- **🔍 Find Similar Files**: Discover related content

### Smart Indexing
- **Automatic caching**: Index built once, reused forever
- **Progress indicators**: Real-time status updates
- **Error handling**: Graceful fallbacks and user feedback

## 📱 CLI Examples

### Build Index (First Time)
```bash
./run_with_ai.sh obsidian_checker_cli.py --build-ai-index --vault ~/Documents/MyVault
```

### Concept Searches
```bash
# Find productivity-related notes
./run_with_ai.sh obsidian_checker_cli.py --ai-search "getting things done"

# Find learning-related content  
./run_with_ai.sh obsidian_checker_cli.py --ai-search "knowledge management"

# Find creative writing notes
./run_with_ai.sh obsidian_checker_cli.py --ai-search "creative process"
```

### Find Similar Files
```bash
./run_with_ai.sh obsidian_checker_cli.py --similar-to "projects/novel-writing.md"
```

## 🎮 Interactive Menu

Run the menu with AI features:
```bash
./run_with_ai.sh obsidian_menu.py
```

**New Menu Option:**
- **7. 🤖 AI Concept Search (Beta)**
  - Guided concept search experience
  - Index building with prompts
  - Similar file discovery

## ⚡ Performance

### First Time Setup
- **Indexing**: 2-5 minutes for 1000 notes
- **Model Download**: ~50MB (automatic, one-time)
- **Storage**: ~2MB per 1000 notes for embeddings

### Ongoing Usage
- **Search Speed**: Nearly instant (<1 second)
- **Memory Usage**: ~100MB during operation
- **Cache**: Persistent between sessions

## 🔄 Comparison: Regular vs AI Search

### Regular Text Search
```bash
# Only finds exact matches
./run_with_ai.sh obsidian_checker_cli.py --search "meditation"
```
**Finds:** Files containing the word "meditation"

### AI Concept Search  
```bash
# Finds conceptually related content
./run_with_ai.sh obsidian_checker_cli.py --ai-search "mindfulness practice"
```
**Finds:** 
- Files about meditation, breathing, awareness
- Notes on stress relief, focus techniques
- Content about mental wellness, contemplation

## 🛠️ Technical Details

### Dependencies Installed
- `sentence-transformers`: Local AI models
- `numpy`: Numerical operations
- `scikit-learn`: Similarity calculations

### File Storage
- **AI Cache**: `.obsidian/ai_search_cache.pkl` (in each vault)
- **Model Cache**: `~/.cache/huggingface/` (system-wide)

### Model Information
- **Model**: `all-MiniLM-L6-v2` by sentence-transformers
- **Size**: ~23MB model + ~50MB dependencies
- **Languages**: Optimized for English, works with other languages
- **Embedding Size**: 384 dimensions per text chunk

## 🎉 Example Use Cases

### 📚 Research & Study
- **Query**: "learning techniques" 
- **Finds**: Spaced repetition, active recall, note-taking methods

### 💼 Project Management
- **Query**: "productivity systems"
- **Finds**: GTD, PARA method, time blocking, project workflows  

### 🧘 Personal Development
- **Query**: "self improvement"
- **Finds**: Habit formation, goal setting, mindfulness, growth mindset

### 📝 Creative Writing
- **Query**: "story structure" 
- **Finds**: Three-act structure, character development, plot devices

## 🔧 Troubleshooting

### AI Not Available Message
If you see "AI search not available", make sure to:
1. Run with `./run_with_ai.sh` script
2. Virtual environment is properly activated
3. Dependencies are installed in the virtual environment

### Slow First Search
- First search builds the index automatically
- Subsequent searches are nearly instant
- Large vaults (1000+ notes) may take a few minutes initially

### Memory Issues
- AI features use ~100MB additional RAM
- Consider closing other applications during index building
- Index is cached, so building only happens once per vault

## 🎊 What's Next?

Your Obsidian Checker now has three powerful search modes:
1. **🔍 Text Search**: Fast keyword matching
2. **🤖 AI Search**: Concept understanding  
3. **🔗 Backlink Check**: Link validation

Perfect for turning your Obsidian vault into an intelligent knowledge discovery system!