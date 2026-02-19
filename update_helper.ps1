param(
    [string]$TargetDir,
    [string]$RepoOwner,
    [string]$RepoName,
    [string]$Branch
)

$ErrorActionPreference = "Stop"

$API_URL = "https://api.github.com/repos/$RepoOwner/$RepoName/git/trees/$Branch`?recursive=1"
$RAW_URL = "https://raw.githubusercontent.com/$RepoOwner/$RepoName/$Branch"

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

try {
    $response = Invoke-RestMethod -Uri $API_URL -UseBasicParsing
} catch {
    Write-Host "[ERROR] Failed to fetch file list: $_" -ForegroundColor Red
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

    $localPath = Join-Path $TargetDir $path
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
