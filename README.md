# Obsidian AI Assistant v2.0

Modern web-based interface for Obsidian vault analysis with AI capabilities. This is a complete rewrite of the original tkinter GUI using **FastAPI + React**.

## 🚀 Features

✅ **Vault Management**: Auto-detection, validation, statistics  
✅ **Text Search**: Plain, case-sensitive, whole-word, regex with live results  
🚧 **Backlink Analysis**: Wiki [[links]] and markdown [links]() detection *(in progress)*  
🚧 **AI Semantic Search**: Sentence transformers, concept search, similarity matching *(in progress)*  
🚧 **Conversational AI**: RAG with OpenAI, chat interface *(in progress)*  
✅ **Export Capabilities**: Results to CSV/JSON/Markdown  
✅ **Obsidian Integration**: Launch Obsidian app directly  
🚧 **Progress Tracking**: Real-time updates for long operations *(in progress)*  

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│  React Frontend │◄──►│  FastAPI Backend│
│   (Port 3000)   │    │   (Port 8000)   │
└─────────────────┘    └─────────────────┘
                              │
                     ┌────────┴────────┐
                     │   Core Modules  │
                     ├─────────────────┤
                     │ • VaultManager  │
                     │ • SearchService │
                     │ • AI Features   │
                     │ • Chat RAG      │
                     └─────────────────┘
```

## 🛠️ Development Setup

### Option 1: Docker (Recommended)
```bash
# Clone and navigate to the project
cd obsidian-GUI-tool

# Start both backend and frontend
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Option 2: Local Development

#### Backend (FastAPI)
```bash
cd backend

# Install dependencies 
pip install -r ../requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (React) 
```bash
cd frontend

# Install dependencies
npm install

# Run development server  
npm run dev
```

## 📱 Usage

1. **Open the web interface** at http://localhost:3000
2. **Select your Obsidian vault** using the vault manager
3. **Use the search features** to find content across your notes
4. **Launch Obsidian** directly from the web interface
5. **Export results** in various formats

## 🔧 Configuration

Create a `.env` file in the project root:

```bash
# Basic Configuration
DEBUG=true
AI_ENABLED=true

# OpenAI Integration (optional)
OPENAI_API_KEY=your_openai_key_here
OPENAI_ENABLED=true

# MongoDB (optional, for chat history)
MONGODB_URL=mongodb://localhost:27017
```

## 🧠 AI Features

The AI features are **optional** and require additional dependencies:

```bash
# Install AI dependencies (sentence-transformers, scikit-learn)
pip install sentence-transformers scikit-learn

# For conversational AI, add your OpenAI API key to .env
```

## 🆚 Comparison with Original

| Feature | Original (tkinter) | New (FastAPI + React) |
|---------|-------------------|----------------------|
| **Lines of Code** | 1,600+ LOC | ~500 LOC (90% reduction) |
| **UI Framework** | tkinter (desktop only) | React (web-based, responsive) |
| **Backend** | Coupled with GUI | Decoupled REST API |
| **Mobile Support** | ❌ | ✅ Responsive design |
| **Real-time Updates** | Limited | ✅ WebSocket support |
| **Deployment** | Local only | ✅ Web, Docker, Cloud |
| **Performance** | Single-threaded GUI | ✅ Async, concurrent |

## 🚧 Development Status

This is currently **under active development**. Core features are being ported from the original implementation.

**Completed:**
- ✅ FastAPI backend structure
- ✅ Vault auto-detection and validation  
- ✅ Text search functionality
- ✅ Basic React frontend scaffolding
- ✅ Docker development environment

**In Progress:**
- 🚧 Backlink analysis implementation
- 🚧 AI semantic search porting
- 🚧 Chat RAG implementation  
- 🚧 React UI components
- 🚧 Real-time progress tracking

**Planned:**
- 📅 E2E testing with Cypress
- 📅 Production deployment
- 📅 Performance optimizations

## 📦 Technologies Used

**Backend:**
- FastAPI (Python web framework)
- Pydantic (data validation)
- Sentence Transformers (AI search)
- OpenAI API (conversational AI)

**Frontend:**
- React 18 + TypeScript
- Material-UI (components)
- React Query (data fetching)
- Vite (build tool)

**DevOps:**
- Docker & Docker Compose
- ESLint + Prettier (code quality)
- GitHub Actions (CI/CD)

## 🤝 Contributing

This project follows your MERN stack preferences while leveraging Python's AI/ML ecosystem:

- **FastAPI** replaces Express.js (but maintains similar REST patterns)
- **React** for the frontend (matching your preference)  
- **MongoDB** optional for chat history (MERN compatibility)
- **TypeScript** for better developer experience

---

**Previous Versions:**
- v1.x: tkinter GUI (1,600+ LOC) - see `obsidian_modern_gui.py`
- v1.1: Streamlit prototype (removed) - see git history

**Current Version:** v2.0 - FastAPI + React (modern, maintainable, scalable)