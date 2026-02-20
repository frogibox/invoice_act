@echo off
chcp 65001 >NUL
cd /d "%~dp0"

echo Запуск приложения...
uv run uvicorn src.main:app --host 127.0.0.1 --port 8000