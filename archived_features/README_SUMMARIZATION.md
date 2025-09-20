# 🤖 AI Summarization Features for Obsidian Checker

## Overview

The Obsidian Checker GUI now includes powerful local AI text summarization capabilities! This feature allows you to:

- **Summarize individual markdown files** from your Obsidian vault
- **Summarize search results** to get quick insights from multiple files
- **Generate different types of summaries** (brief, auto, detailed, key points)
- **Export summaries** to markdown files with metadata
- **Work completely offline** - no internet required once models are downloaded
- **Cache summaries** to avoid re-processing the same content

## 🚀 Quick Start

### 1. Install Dependencies

First, install the required AI libraries:

```bash
pip install -r requirements.txt
```

This will install:
- `transformers` - Hugging Face transformers library
- `torch` - PyTorch for running the AI models
- Other dependencies automatically

### 2. Test Your Installation

Run the test script to verify everything works:

```bash
python test_summarization.py
```

### 3. Run the GUI

Launch the main application:

```bash
python obsidian_backlink_checker.py
```

The AI Summarization section will appear if dependencies are properly installed.

## 📖 How to Use

### In the GUI

1. **Select your Obsidian vault** using the Browse button
2. Navigate to the **"📝 AI Text Summarization"** section
3. Choose your **summary type**:
   - **Auto**: Balanced summary (~130 words)
   - **Brief**: Short summary (~50 words) 
   - **Detailed**: Longer summary (~300 words)
   - **Key Points**: Focused on main points (~200 words)

#### Summarize a File
1. Enter a file path (e.g., `notes/my-note.md`) or leave blank to be prompted
2. Click **"📄 Summarize File"**
3. Wait for the AI model to load and process (first run takes longer)
4. View the summary in the results area

#### Summarize Search Results
1. First, perform a search using the **Search** section
2. Once you have search results, click **"🔍 Summarize Search Results"**
3. The AI will create a summary combining insights from all matching files

#### Export Summaries
1. After generating a summary, click **"💾 Export Summary"**
2. Save as a markdown file with full metadata and statistics

### Standalone Usage

You can also use the summarization module directly:

```bash
python obsidian_ai_summarizer.py
```

This provides a command-line interface for testing and batch processing.

## 🔧 Technical Details

### Models Available

The system supports multiple AI models, optimized for different use cases:

| Model | Size | Speed | Quality | Recommended |
|-------|------|-------|---------|-------------|
| **DistilBART** | ~268MB | Fast | Good | ✅ Yes (Default) |
| **BART-Large** | ~1.6GB | Slower | Excellent | For high-quality needs |
| **FLAN-T5-Small** | ~80MB | Very Fast | Basic | For quick processing |

### Caching System

- Summaries are **automatically cached** to avoid reprocessing
- Cache location: `{vault}/.obsidian/ai_summaries/`
- Cache files include metadata and are valid for 30 days
- Use different cache keys for different summary types

### Text Processing

The system automatically:
- **Cleans markdown formatting** while preserving content
- **Splits long texts** into chunks that fit model limits
- **Combines chunk summaries** for very long documents
- **Handles various file encodings** gracefully

### Performance Tips

- **First run**: Model download takes time (~1-2 minutes for DistilBART)
- **Subsequent runs**: Much faster as models are cached locally
- **GPU acceleration**: Automatically used if CUDA is available
- **Memory usage**: ~2-4GB RAM during summarization

## 📊 Example Output

```
📝 Summarizing file: research/ai-ethics.md
   Summary type: auto
============================================================

✅ Summary:
The document discusses the ethical implications of artificial 
intelligence development, focusing on bias in algorithms, privacy 
concerns, and the need for responsible AI development practices. 
It emphasizes the importance of transparency, accountability, and 
human oversight in AI systems.

ℹ️ Summary Statistics:
   Original length: 12,847 characters
   Summary length: 287 characters
   Compression ratio: 2.2%
   Chunks processed: 3
   Model used: distilbart
============================================================
```

## 🛠️ Troubleshooting

### Common Issues

**"Summarization dependencies not installed"**
- Run: `pip install transformers torch`
- Ensure you have Python 3.8+ 

**"Failed to load summarization model"**
- Check internet connection for initial download
- Ensure you have ~2GB free disk space
- Try clearing cache: delete `{vault}/.obsidian/ai_summaries/`

**"Out of memory"**
- Close other applications
- Try the smaller FLAN-T5-Small model
- Process shorter texts

**Slow performance**
- Models download once, then cache locally
- GPU acceleration helps but not required
- Subsequent runs are much faster

### Model Download Locations

Models are cached automatically by Hugging Face:
- **macOS**: `~/.cache/huggingface/transformers/`
- **Linux**: `~/.cache/huggingface/transformers/`
- **Windows**: `%USERPROFILE%\.cache\huggingface\transformers\`

## 🔍 Advanced Usage

### Custom Text Summarization

```python
from obsidian_ai_summarizer import ObsidianAISummarizer

# Initialize
summarizer = ObsidianAISummarizer("/path/to/vault")

# Summarize text directly  
result = summarizer.summarize_text("Your text here...", "auto")
print(result['summary'])

# Summarize file
result = summarizer.summarize_file("notes/file.md", "brief")

# Check cache stats
stats = summarizer.get_summary_stats()
print(f"Cached summaries: {stats['total_summaries']}")
```

### Batch Processing

```python
import os
from pathlib import Path

vault_path = "/path/to/vault"
summarizer = ObsidianAISummarizer(vault_path)

# Process all markdown files
for md_file in Path(vault_path).rglob("*.md"):
    rel_path = str(md_file.relative_to(vault_path))
    result = summarizer.summarize_file(rel_path, "auto")
    if 'summary' in result:
        print(f"{rel_path}: {result['summary'][:100]}...")
```

## 🔒 Privacy & Security

- **Fully offline**: No data sent to external services
- **Local processing**: AI models run on your machine
- **Vault privacy**: Content never leaves your computer
- **No tracking**: No usage analytics or data collection

## 🆚 Comparison with Cloud Solutions

| Feature | Local AI | OpenAI/Cloud |
|---------|----------|--------------|
| Privacy | ✅ Complete | ❌ Data sent externally |
| Cost | ✅ Free after setup | 💰 Per-use charges |
| Internet | ✅ Works offline | ❌ Requires connection |
| Speed | ⚡ Fast after load | ⚡ Very fast |
| Quality | ✅ Good | ✅ Excellent |
| Setup | 🔧 Some setup needed | ✅ Immediate |

## 📈 Performance Benchmarks

Based on typical Obsidian notes (~1000-3000 characters):

- **Brief summaries**: 2-5 seconds
- **Auto summaries**: 3-8 seconds  
- **Detailed summaries**: 5-15 seconds
- **Very long documents** (>10k chars): 15-60 seconds

*Times after initial model loading. First run includes model download time.*

## 🤝 Contributing

The summarization system is designed to be extensible:

- **Add new models**: Modify `MODELS` dict in `obsidian_ai_summarizer.py`
- **Custom summary types**: Extend `summarize_text()` method
- **New export formats**: Add formats to `export_summary_results()`
- **Enhanced preprocessing**: Improve `clean_text_for_summarization()`

## 📋 Changelog

### v1.0.0 - Initial Release
- ✅ Local DistilBART summarization
- ✅ Multiple summary types
- ✅ GUI integration
- ✅ Caching system
- ✅ Export functionality
- ✅ Search results summarization

### Planned Features
- 🔄 Batch file processing
- 🔄 Custom model selection in GUI
- 🔄 Summary comparison tools
- 🔄 Integration with existing backlink analysis

---

*Happy summarizing! 🎉*

For issues or questions, check the main README or create a GitHub issue.