#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> VoiceTyping build started" -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Pip = Join-Path $Root ".venv\Scripts\pip.exe"

Write-Host "==> Installing dependencies..."
& $Pip install -q -e .
& $Pip install -q -r requirements-dev.txt

Write-Host "==> Generating icon..."
& $Python scripts/generate_icon.py

Write-Host "==> Running PyInstaller (this may take several minutes)..."
& $Python -m PyInstaller --noconfirm VoiceTyping.spec

$DistDir = Join-Path $Root "dist\VoiceTyping"
$ExePath = Join-Path $DistDir "VoiceTyping.exe"

if (Test-Path $ExePath) {
    Write-Host ""
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Output: $DistDir"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Run dist\VoiceTyping\VoiceTyping.exe to test"
    Write-Host "  2. Optional: install Inno Setup and compile installer\VoiceTyping.iss"
    Write-Host "  3. Zip dist\VoiceTyping folder for portable distribution"
} else {
    Write-Host "Build failed: VoiceTyping.exe not found." -ForegroundColor Red
    exit 1
}
