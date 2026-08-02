@echo off
REM ICMS Backend Startup Script for Windows

echo 🚀 Starting ICMS Backend Server...

REM Check if virtual environment exists
if not exist "venv" (
    echo ⚠️  Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo ✅ .env file created - please update with your settings
)

REM Install dependencies if needed
if not exist "venv\installed" (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
    type nul > venv\installed
    echo ✅ Dependencies installed
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads

REM Run the server
echo 🌐 Server starting at http://localhost:8000
echo 📚 API Docs available at http://localhost:8000/docs
echo.
python core\main.py
