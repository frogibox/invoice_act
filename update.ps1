# update.ps1 - Update Invoice Act Tracker without Git
# Run: powershell -ExecutionPolicy Bypass -File update.ps1

$ErrorActionPreference = "Stop"

$REPO_OWNER = "frogibox"
$REPO_NAME = "invoice_act"
$BRANCH = "main"
$API_URL = "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/git/trees/${BRANCH}?recursive=1"
$RAW_URL = "https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/$BRANCH"

$EXCLUDE_PATTERNS = @(
    "\.coverage$",
    "uv\.lock$",
    "test_results\.html$",
    "\.db$",
    "\.db-journal$",
    "__pycache__",
    "\.pyc$",
    "backup/"
)

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Invoice Act Tracker - Update" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "Fetching file list from GitHub..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri $API_URL -UseBasicParsing
} catch {
    Write-Host "[ERROR] Failed to fetch file list: $_" -ForegroundColor Red
    pause
    exit 1
}

$files = $response.tree | Where-Object { $_.type -eq "blob" }

$updated = 0
$skipped = 0
$errors = 0

foreach ($file in $files) {
    $path = $file.path

    $skip = $false
    foreach ($pattern in $EXCLUDE_PATTERNS) {
        if ($path -match $pattern) {
            $skip = $true
            break
        }
    }
    if ($skip) {
        $skipped++
        continue
    }

    $localPath = Join-Path $PSScriptRoot $path
    $dir = Split-Path $localPath -Parent

    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    try {
        $url = "$RAW_URL/$path"
        Invoke-WebRequest -Uri $url -OutFile $localPath -UseBasicParsing
        Write-Host "  [OK] $path" -ForegroundColor Green
        $updated++
    } catch {
        Write-Host "  [ERROR] $path : $_" -ForegroundColor Red
        $errors++
    }
}

Write-Host ""
Write-Host "Updated: $updated | Skipped: $skipped | Errors: $errors" -ForegroundColor Cyan
Write-Host ""

Write-Host "Syncing dependencies..." -ForegroundColor Cyan
where.exe uv >$null 2>$null
if ($LASTEXITCODE -eq 0) {
    uv sync
} else {
    Write-Host "[WARNING] uv not found, skipping dependency sync" -ForegroundColor Yellow
}

Write-Host ""

Write-Host "Stopping uvicorn on port 8000..." -ForegroundColor Cyan
$connections = netstat -ano | Select-String ":8000\s+.*LISTENING"
foreach ($conn in $connections) {
    $pid = ($conn -split '\s+')[-1]
    taskkill /F /PID $pid 2>$null | Out-Null
}
Start-Sleep -Seconds 2

Write-Host "Starting application..." -ForegroundColor Cyan
Start-Process cmd -ArgumentList "/c", ".venv\Scripts\uvicorn.exe src.main:app --host 127.0.0.1 --port 8000" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Update completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
pause
