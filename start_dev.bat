@echo off
REM Writingway Web Development Startup Script for Windows

echo 🚀 Starting Writingway Web Development Environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

REM Create virtual environment for backend if it doesn't exist
if not exist "backend\venv" (
    echo 📦 Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

REM Activate virtual environment and install backend dependencies
echo 📦 Installing backend dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️ Creating backend .env file...
    copy .env.example .env
    echo Please edit backend\.env file with your configuration
)

REM Start backend server
echo 🔧 Starting backend server...
start "Backend Server" cmd /k "venv\Scripts\activate.bat && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
cd ..

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
if not exist "node_modules" (
    npm install
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️ Creating frontend .env file...
    copy .env.example .env
)

REM Start frontend server
echo 🎨 Starting frontend server...
start "Frontend Server" cmd /k "npm start"
cd ..

echo.
echo ✅ Writingway Web is starting up!
echo.
echo 📍 Backend API: http://localhost:8000
echo 📍 Frontend App: http://localhost:3000
echo 📍 API Documentation: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul
