@echo off
setlocal enabledelayedexpansion
title CineMind - Development Server

echo =====================================================================
echo              C I N E M I N D   (Dev Mode)
echo    Backend (FastAPI): http://127.0.0.1:8000
echo    Frontend (Vite):   http://localhost:5173
echo =====================================================================
echo.

cd /d "%~dp0"

:: Start FastAPI Backend in background window
echo Starting FastAPI Backend server...
start "CineMind Backend (FastAPI)" cmd /k ".\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

:: Start Vite Frontend dev server
echo Starting Vite Frontend dev server...
cd frontend
start "CineMind Frontend (Vite)" cmd /k "npm.cmd run dev"

:: Open browser to frontend after 3 seconds
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:5173"

echo Both dev servers launched!

