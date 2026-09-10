@echo off
echo =========================================================================
echo Starting APIx: Real-time Airfare Price Index Platform for India
echo Ministry of Statistics and Programme Implementation (MoSPI) - RBI CPI Platform
echo =========================================================================

REM Navigate to project root
cd /d "%~dp0\.."

REM Initialize and seed database if necessary
echo [1/3] Checking Database and Reference Data...
python -m backend.scripts.seed_database

REM Launch FastAPI Backend in a separate window
echo [2/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "APIx Backend (FastAPI)" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

REM Launch React Frontend in a separate window
echo [3/3] Starting React Dashboard on http://localhost:5173 ...
start "APIx Frontend (Vite)" cmd /k "cd frontend && npm.cmd run dev"

echo =========================================================================
echo APIx Platform is running!
echo - Dashboard UI:      http://localhost:5173
echo - Backend API Docs:  http://127.0.0.1:8000/docs
echo =========================================================================
pause
