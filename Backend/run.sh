#!/bin/bash
# ICMS Backend Startup Script

echo "🚀 Starting ICMS Backend Server..."

# Kill any existing process on port 8000
echo "🔍 Checking for existing server on port 8000..."
PID=$(lsof -ti:8000)
if [ ! -z "$PID" ]; then
    echo "⚠️  Found existing process (PID: $PID), stopping it..."
    kill -9 $PID 2>/dev/null
    sleep 1
    echo "✅ Stopped existing server"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo "✅ .env file created - please update with your settings"
fi

# Install dependencies if requirements.txt was modified
DEPS_MARKER="venv/.deps_installed"
if [ ! -f "$DEPS_MARKER" ] || [ "requirements.txt" -nt "$DEPS_MARKER" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch "$DEPS_MARKER"
        echo "✅ Dependencies installed"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
else
    echo "✅ Dependencies up to date"
fi

# Create necessary directories
mkdir -p logs uploads

# Run the server
echo "🌐 Server starting at http://localhost:8000"
echo "📚 API Docs available at http://localhost:8000/docs"
echo ""
python -m uvicorn core.main:app --host 127.0.0.1 --port 8000 --reload
