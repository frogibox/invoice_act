@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo Загрузка обновлений...

:: Сброс файла блокировки при наличии локальных изменений
git diff --name-only | findstr "uv.lock" >nul
if not errorlevel 1 git checkout -- uv.lock

:: Проверка и сохранение локальных изменений
git diff --quiet HEAD
if errorlevel 1 (
    git stash push -m "Auto-save before update"
    set STASHED=1
) else (
    set STASHED=0
)

:: Получение изменений с сервера
git pull origin main

:: Возврат локальных изменений
if "%STASHED%"=="1" git stash pop

echo Синхронизация зависимостей...
uv sync

echo Остановка текущего процесса...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

echo Запуск приложения...
start "Invoice Act" cmd /c "uv run uvicorn src.main:app --host 127.0.0.1 --port 8000"