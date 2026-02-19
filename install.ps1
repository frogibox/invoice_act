$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/frogibox/invoice_act.git"

$DefaultPath = Join-Path $env:USERPROFILE "invoice_act"
$UserInput = Read-Host "Введите путь для установки (или нажмите Enter для установки по умолчанию: $DefaultPath)"
$InstallDir = if ([string]::IsNullOrWhiteSpace($UserInput)) { $DefaultPath } else { $UserInput }

Write-Host "Проверка наличия Git..."
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git не найден. Выполняется установка..."
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
    $env:Path += ";C:\Program Files\Git\cmd"
}

Write-Host "Проверка наличия uv..."
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv не найден. Выполняется установка..."
    Invoke-RestMethod -Uri https://astral.sh/uv/install.ps1 | Invoke-Expression
    $env:Path += ";$HOME\.cargo\bin"
}

if (Test-Path (Join-Path $InstallDir ".git")) {
    Write-Host "Директория существует. Выполняется обновление репозитория..."
    Set-Location $InstallDir
    git fetch origin main
    git reset --hard origin/main
} else {
    Write-Host "Клонирование репозитория..."
    git clone $RepoUrl $InstallDir
    Set-Location $InstallDir
}

Write-Host "Установка зависимостей..."
uv sync

Write-Host "Установка завершена. Рабочая директория: $InstallDir"