#!/bin/bash

# Writingway Web Development Startup Script

echo "🚀 Starting Writingway Web Development Environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Create virtual environment for backend if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment and install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating backend .env file..."
    cp .env.example .env
    echo "Please edit backend/.env file with your configuration"
fi

# Start backend server in background
echo "🔧 Starting backend server..."
uvicorn main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating frontend .env file..."
    cp .env.example .env
fi

# Start frontend server
echo "🎨 Starting frontend server..."
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Writingway Web is starting up!"
echo ""
echo "📍 Backend API: http://localhost:8001"
echo "📍 Frontend App: http://localhost:3000"
echo "📍 API Documentation: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
