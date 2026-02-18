# install.ps1 - Скрипт установки Invoice Act Tracker
# Запуск: irm https://raw.githubusercontent.com/frogibox/invoice_act/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$REPO_OWNER = "frogibox"
$REPO_NAME = "invoice_act"
$REPO_URL = "https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/main"

# Файлы репозитория для скачивания (исключая .coverage, uv.lock, test_results.html)
$FILES = @(
    ".gitignore",
    "1_install_uv.bat",
    "2_setup.bat",
    "3_run.bat",
    "AGENTS.md",
    "README.md",
    "clear_database.bat",
    "clear_database.py",
    "clone_rep.bat",
    "clone_repo.bat",
    "git_status.bat",
    "pyproject.toml",
    "restore_database.bat",
    "restore_database.py",
    "run_e2e.bat",
    "run_tests.bat",
    "src/__init__.py",
    "src/database.py",
    "src/main.py",
    "src/static/css/bootstrap.min.css",
    "src/static/js/bootstrap.bundle.min.js",
    "src/templates/contractor.html",
    "src/templates/dashboard.html",
    "src/templates/employees.html",
    "src/templates/import.html",
    "src/templates/linked_acts.html",
    "src/templates/nav.html",
    "src/templates/unlinked_acts.html",
    "e2e/__init__.py",
    "e2e/conftest.py",
    "e2e/test_dashboard.py",
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/integration/__init__.py",
    "tests/integration/test_api.py",
    "tests/unit/__init__.py",
    "tests/unit/test_utils.py"
)

function Install-UvIfMissing {
    Write-Host "Проверка uv..." -ForegroundColor Cyan
    $uvCheck = Get-Command uv -ErrorAction SilentlyContinue
    if (-not $uvCheck) {
        Write-Host "uv не найден. Устанавливаю..." -ForegroundColor Yellow
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
    Write-Host "uv: " -NoNewline
    uv --version
}

function Get-InstallationPath {
    $defaultPath = Join-Path $env:USERPROFILE "invoice_act"
    Write-Host "Путь для установки (по умолчанию: $defaultPath): " -NoNewline
    $userInput = Read-Host
    if ([string]::IsNullOrWhiteSpace($userInput)) {
        return $defaultPath
    }
    return $userInput
}

function Download-File {
    param(
        [string]$File,
        [string]$Path
    )
    
    $url = "$REPO_URL/$File"
    $localPath = Join-Path $Path $File
    $dir = Split-Path $localPath -Parent
    
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $localPath -UseBasicParsing
        Write-Host "  [OK] $File" -ForegroundColor Green
    } catch {
        Write-Host "  [ОШИБКА] $File : $_" -ForegroundColor Red
    }
}

function Download-ProjectFiles {
    param([string]$Path)
    
    Write-Host "Скачивание файлов проекта..." -ForegroundColor Cyan
    
    foreach ($file in $FILES) {
        Download-File -File $file -Path $Path
    }
    
    Write-Host "Файлы проекта скачаны." -ForegroundColor Green
}

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Invoice Act Tracker - Установка" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

# 1. Проверить/установить uv
Install-UvIfMissing
Write-Host ""

# 2. Выбрать путь установки
$installPath = Get-InstallationPath

# 3. Создать директорию
if (-not (Test-Path $installPath)) {
    New-Item -ItemType Directory -Path $installPath -Force | Out-Null
}
Set-Location $installPath
Write-Host "Установка в: $installPath" -ForegroundColor Cyan
Write-Host ""

# 4. Скачать файлы проекта
Download-ProjectFiles -Path $installPath
Write-Host ""

# 5. Установить зависимости
Write-Host "Установка зависимостей..." -ForegroundColor Cyan
uv sync
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "  Установка завершена!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Запуск приложения:" -ForegroundColor Cyan
Write-Host "  uv run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload" -ForegroundColor White
