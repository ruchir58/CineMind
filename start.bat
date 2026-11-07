@echo off
setlocal enabledelayedexpansion
title CineMind - AI-Powered Entertainment Discovery Platform

echo =====================================================================
echo                       C I N E M I N D
echo     AI-Powered Movie ^& TV Show Discovery ^& Recommendation Platform
echo =====================================================================
echo.

:: Change directory to script folder
cd /d "%~dp0"

:: 1. Check Python virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Setting up Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Python not found or failed to create .venv. Please ensure Python 3.10+ is installed.
        pause
        exit /b 1
    )
    echo [INFO] Installing backend dependencies...
    .\.venv\Scripts\pip.exe install -r requirements.txt
) else (
    echo [1/4] Python virtual environment detected.
)

:: 2. Check if ML models and datasets are prepared
if not exist "backend\models\tfidf_model.joblib" (
    echo [2/4] Training recommendation models and semantic embeddings...
    .\.venv\Scripts\python.exe scripts/preprocess.py
) else (
    echo [2/4] Recommendation models and vector embeddings verified.
)

:: 3. Check if frontend is built
if not exist "frontend\dist\index.html" (
    echo [3/4] Building React frontend with Vite...
    cd frontend
    if not exist "node_modules" (
        echo [INFO] Installing frontend dependencies...
        call npm.cmd install
    )
    call npm.cmd run build
    cd ..
) else (
    echo [3/4] Production frontend build verified.
)

:: 4. Launch Application
echo [4/4] Starting CineMind Server at http://127.0.0.1:8000 ...
echo.
echo =====================================================================
echo  CineMind is now live at: http://127.0.0.1:8000
echo  Press Ctrl+C anytime to stop the server.
echo =====================================================================
echo.

:: Automatically open default browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000"

:: Run FastAPI with Uvicorn
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

pause

