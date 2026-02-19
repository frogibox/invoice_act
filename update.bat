@echo off
setlocal enabledelayedexpansion

:: --- SETTINGS ---
set REPO_OWNER=frogibox
set REPO_NAME=invoice_act
set BRANCH=main

echo ========================================
echo   Invoice Act Tracker - Update
echo   (no Git, via GitHub API)
echo ========================================
echo.

:: 1. CHECK POWERSHELL
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] PowerShell not found
    pause
    exit /b 1
)

:: 2. FETCH FILE LIST AND DOWNLOAD
echo [INFO] Fetching file list and downloading...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0update_helper.ps1" "%~dp0" "%REPO_OWNER%" "%REPO_NAME%" "%BRANCH%"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to update files
    pause
    exit /b 1
)

:: 3. SYNC DEPENDENCIES
echo.
echo [INFO] Syncing dependencies...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] uv not found, skipping dependency sync
    goto :restart
)

uv sync
if %errorlevel% neq 0 (
    echo [WARNING] uv sync failed
)

:: 4. RESTART APPLICATION
:restart
echo.
echo ========================================
echo   Restarting application
echo ========================================
echo.

echo Stopping uvicorn on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

echo Starting application...
start "PIPISKA" cmd /c ".venv\Scripts\uvicorn.exe src.main:app --host 127.0.0.1 --port 8000"

echo.
echo ========================================
echo   Update completed!
echo ========================================
pause
exit /b 0
