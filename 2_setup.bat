@echo off
echo Checking for uv...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv is not installed.
    echo Please install uv from: https://github.com/astral-sh/uv
    echo Or run: pip install uv
    pause
    exit /b 1
)

echo Installing dependencies with uv...
call uv sync

if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
pause
