#!/bin/bash

# Tech News Tracker with Hourly Updates
# This script runs the API server and scheduler together

echo "🚀 Starting Tech News Tracker with Hourly Updates..."

# Activate virtual environment
source venv/bin/activate

# Kill any existing processes
pkill -f "tech_scheduler.py" 2>/dev/null
pkill -f "uvicorn main:app" 2>/dev/null

# Start the hourly scheduler in background
echo "⏰ Starting hourly tech news scheduler..."
python tech_scheduler.py --daemon &
SCHEDULER_PID=$!

# Wait a moment for scheduler to start
sleep 2

# Start the API server
echo "🌐 Starting API server..."
echo "=========================================="
echo "🎯 Tech News Tracker is now running!"
echo "📱 Web Interface: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "⏰ Auto-updates: Every hour"
echo "🛑 Press Ctrl+C to stop"
echo "=========================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Tech News Tracker..."
    kill $SCHEDULER_PID 2>/dev/null
    pkill -f "uvicorn main:app" 2>/dev/null
    echo "✅ Stopped successfully"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start API server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
