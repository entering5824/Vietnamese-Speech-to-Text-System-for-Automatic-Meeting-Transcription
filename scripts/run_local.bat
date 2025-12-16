@echo off
REM Script để chạy ứng dụng local trên Windows

echo 🚀 Vietnamese Speech-to-Text System - Local Setup
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

cd /d "%PROJECT_DIR%"

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist "temp" mkdir temp
if not exist "export" mkdir export

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from env.example...
    if exist "env.example" (
        copy env.example .env
        echo ✅ Created .env file. Please update it with your settings.
    )
)

REM Run Streamlit app
echo 🎉 Starting Streamlit app...
echo 📍 App will be available at: http://localhost:8501
echo.

streamlit run app/main.py

pause

