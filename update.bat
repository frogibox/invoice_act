@echo off
setlocal enabledelayedexpansion

:: --- НАСТРОЙКИ ---
set REPO_OWNER=frogibox
set REPO_NAME=invoice_act
set BRANCH=main
set RAW_URL=https://raw.githubusercontent.com/%REPO_OWNER%/%REPO_NAME%/%BRANCH%
set API_URL=https://api.github.com/repos/%REPO_OWNER%/%REPO_NAME%/git/trees/%BRANCH%?recursive=1

echo ========================================
echo   Invoice Act Tracker - Обновление
echo   (без Git, через GitHub API)
echo ========================================
echo.

:: 1. ПРОВЕРКА POWERSHELL (нужен для работы с JSON API)
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo [ОШИБКА] PowerShell не найден
    pause
    exit /b 1
)

:: 2. ПОЛУЧЕНИЕ СПИСКА ФАЙЛОВ И СКАЧИВАНИЕ
echo [INFO] Получение списка файлов и скачивание...
echo.

powershell -ExecutionPolicy Bypass -Command ^
    "$ErrorActionPreference = 'Stop'; " ^
    "$api = '%API_URL%'; " ^
    "$raw = '%RAW_URL%'; " ^
    "$exclude = @('\.coverage$','uv\.lock$','test_results\.html$','\.db$','\.db-journal$','__pycache__','\.pyc$','backup/'); " ^
    "$resp = Invoke-RestMethod -Uri $api -UseBasicParsing; " ^
    "$files = $resp.tree | Where-Object { $_.type -eq 'blob' }; " ^
    "$ok = 0; $skip = 0; $err = 0; " ^
    "foreach ($f in $files) { " ^
    "  $p = $f.path; $s = $false; " ^
    "  foreach ($ex in $exclude) { if ($p -match $ex) { $s = $true; break } }; " ^
    "  if ($s) { $skip++; continue }; " ^
    "  $lp = Join-Path '%~dp0' $p; " ^
    "  $d = Split-Path $lp -Parent; " ^
    "  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }; " ^
    "  try { Invoke-WebRequest -Uri \"$raw/$p\" -OutFile $lp -UseBasicParsing; Write-Host \"  [OK] $p\" -ForegroundColor Green; $ok++ } " ^
    "  catch { Write-Host \"  [ОШИБКА] $p : $_\" -ForegroundColor Red; $err++ } " ^
    "}; " ^
    "Write-Host ''; Write-Host \"Обновлено: $ok | Пропущено: $skip | Ошибок: $err\" -ForegroundColor Cyan"

if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Не удалось обновить файлы
    pause
    exit /b 1
)

:: 3. СИНХРОНИЗАЦИЯ ЗАВИСИМОСТЕЙ
echo.
echo [INFO] Синхронизация зависимостей...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [ПРЕДУПРЕЖДЕНИЕ] uv не найден, пропуск синхронизации
    goto :restart
)

uv sync
if %errorlevel% neq 0 (
    echo [ПРЕДУПРЕЖДЕНИЕ] uv sync завершился с ошибкой
)

:: 4. ПЕРЕЗАПУСК ПРИЛОЖЕНИЯ
:restart
echo.
echo ========================================
echo   Перезапуск приложения
echo ========================================
echo.

echo Останавливаю uvicorn на порту 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

echo Запускаю приложение...
start "PIPISKA" cmd /c ".venv\Scripts\uvicorn.exe src.main:app --host 127.0.0.1 --port 8000"

echo.
echo ========================================
echo   Обновление завершено!
echo ========================================
pause
exit /b 0
