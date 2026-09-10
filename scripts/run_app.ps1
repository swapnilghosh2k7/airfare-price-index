# APIx Platform Launcher for PowerShell
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "Starting APIx: Real-time Airfare Price Index Platform for India" -ForegroundColor Yellow
Write-Host "Ministry of Statistics and Programme Implementation (MoSPI) - RBI CPI Platform" -ForegroundColor Cyan
Write-Host "========================================================================="

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "[1/3] Initializing and Seeding Database..." -ForegroundColor Green
python -m backend.scripts.seed_database

Write-Host "[2/3] Starting FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ProjectRoot'; python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "[3/3] Starting React Dashboard on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ProjectRoot\frontend'; npm.cmd run dev"

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "APIx Platform Started Successfully!" -ForegroundColor Green
Write-Host "Dashboard:      http://localhost:5173" -ForegroundColor Yellow
Write-Host "FastAPI Docs:   http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "=========================================================================" -ForegroundColor Cyan
