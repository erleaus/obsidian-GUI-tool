# OpenAI Integration Setup Guide

## 🎯 What This Adds

Your Obsidian tool now has **conversational AI capabilities**! You can:

- **Ask natural language questions** about your vault content
- **Get summaries** of topics across all your notes  
- **Discover connections** between different notes
- **Stream responses** in real-time
- **Export conversations** for future reference

### Example Queries
- *"Summarize all notes I have on climate change"* → *"You have no notes on climate change"*
- *"What are my thoughts on productivity?"* → *Synthesizes content from all productivity-related notes*
- *"Show me notes about machine learning"* → *Finds and summarizes relevant content*
- *"What connections exist between my psychology and philosophy notes?"*

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
# Install OpenAI dependencies
pip install openai python-dotenv tiktoken

# Or install everything at once
pip install -r requirements.txt
```

### 2. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create account or sign in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

### 3. Configure Your API Key

**Option A: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Option B: Create .env File**
```bash
# Copy the template
cp .env.template .env

# Edit .env and add your key
OPENAI_API_KEY=your_actual_api_key_here
```

### 4. Test the Setup

```bash
# Test conversational AI
python3 obsidian_conversation.py

# Test OpenAI client directly
python3 openai_client.py
```

## 💡 Usage Examples

### Interactive Chat Mode
```bash
python3 obsidian_checker_cli.py --chat --vault /path/to/vault
```

### Single Questions
```bash
# Ask a question (with streaming)
python3 obsidian_checker_cli.py --ask "What are my thoughts on productivity?" --stream

# Get vault summary
python3 obsidian_checker_cli.py --vault-summary

# Suggest connections
python3 obsidian_checker_cli.py --suggest-connections
```

### Integration with Existing AI Search
```bash
# Build AI index first (if not already done)
python3 obsidian_checker_cli.py --build-ai-index

# Then use conversational AI
python3 obsidian_checker_cli.py --chat
```

## ⚙️ Configuration Options

Edit your `.env` file to customize:

```bash
# OpenAI Model (gpt-4o-mini is fast and cheap)
OPENAI_MODEL=gpt-4o-mini
# Or use gpt-4o for better quality (more expensive)
# OPENAI_MODEL=gpt-4o

# Response creativity (0.0-2.0)
OPENAI_TEMPERATURE=0.7

# Max response length
OPENAI_MAX_TOKENS=4096

# How many note chunks to include as context
MAX_CONTEXT_CHUNKS=10

# Similarity threshold for note retrieval
SIMILARITY_THRESHOLD=0.3
```

## 💰 Cost Estimation

**gpt-4o-mini** (recommended for most users):
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- **Typical query cost: $0.01 - $0.05**

**gpt-4o** (higher quality):
- Input: $2.50 per 1M tokens  
- Output: $10.00 per 1M tokens
- **Typical query cost: $0.10 - $0.50**

### Cost Tips:
- Start with `gpt-4o-mini` for testing
- Use `--stream` flag to see responses as they generate
- Monitor usage in OpenAI dashboard

## 🔧 Troubleshooting

### "OpenAI dependencies not installed"
```bash
pip install openai python-dotenv tiktoken
```

### "OpenAI API key not found"
```bash
# Check your environment variable
echo $OPENAI_API_KEY

# Or check your .env file
cat .env
```

### "AI search not available"
```bash
# Install semantic search dependencies
pip install sentence-transformers numpy scikit-learn

# Build the AI index
python3 obsidian_checker_cli.py --build-ai-index
```

### "Authentication failed"
- Double-check your API key is correct
- Make sure you have credits in your OpenAI account
- Try testing with a simple question first

### "Rate limit exceeded"
- Wait a minute and try again
- Consider upgrading your OpenAI plan
- The tool automatically handles rate limits with retries

## 🎪 Advanced Features

### Export Conversations
```bash
# In chat mode, type 'stats' to see usage
# Conversations are automatically saved in memory

# Export programmatically:
python3 -c "
from obsidian_conversation import ObsidianConversation
conv = ObsidianConversation('/path/to/vault')
# Use the conversation, then:
print(conv.export_conversation('markdown'))
"
```

### Custom System Prompts
Edit `obsidian_conversation.py` around line 51 to customize how the AI behaves.

### Multiple Vaults
```bash
# Use different vaults
python3 obsidian_checker_cli.py --vault /path/to/vault1 --chat
python3 obsidian_checker_cli.py --vault /path/to/vault2 --chat
```

## 🔐 Privacy & Security

- **Your notes stay local** - only relevant snippets are sent to OpenAI
- **API calls are encrypted** in transit
- **No data is stored** by OpenAI for training (with API usage)
- **Consider using .env files** instead of environment variables for better security
- **Review what gets sent** - the tool shows you what context is being used

## 🚀 What's Next?

This is just the beginning! Future enhancements could include:

- **Web interface** with React (matching your MERN preference)
- **Obsidian plugin** integration
- **Advanced RAG features** like document chunking strategies
- **Multi-modal support** for images in notes
- **Custom model fine-tuning** on your specific vault

## 🆘 Need Help?

1. **Check the error messages** - they usually contain helpful information
2. **Test each component separately** - AI search, then OpenAI client, then conversation
3. **Start with simple queries** before trying complex ones
4. **Monitor your OpenAI usage** in the dashboard to track costs

---

**Ready to get started?** Run this to test everything:

```bash
python3 obsidian_checker_cli.py --vault /path/to/your/vault --ask "What topics do my notes cover?" --stream
```