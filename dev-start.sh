#!/bin/bash
# Development startup script for Obsidian AI Assistant v2.0

echo "🚀 Starting Obsidian AI Assistant v2.0 Development Environment"
echo "============================================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker to continue."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose to continue."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

echo "🐳 Starting services with Docker Compose..."
echo "   - Backend (FastAPI): http://localhost:8000"
echo "   - Frontend (React): http://localhost:3000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""

# Start the development environment
docker-compose up --build

echo ""
echo "👋 Development environment stopped"