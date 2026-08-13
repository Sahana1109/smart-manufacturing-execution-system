# SmartMES Development Environment Setup Script (Windows PowerShell)

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "      SmartMES Development Setup Assistant       " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Environment File Check
if (-not (Test-Path -Path ".env")) {
    Write-Host "[+] Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item -Path ".env.example" -Destination ".env"
} else {
    Write-Host "[✓] .env file exists." -ForegroundColor Green
}

# 2. Backend Virtual Environment Setup
Write-Host "`n[+] Checking Backend Python Environment..." -ForegroundColor Yellow
Set-Location -Path "backend"
if (-not (Test-Path -Path "venv")) {
    Write-Host "[+] Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}
Write-Host "[+] Installing/Updating backend Python dependencies..." -ForegroundColor Yellow
.\venv\Scripts\pip.exe install --upgrade pip
.\venv\Scripts\pip.exe install -r requirements.txt
Set-Location -Path ".."

# 3. Frontend Node Setup
Write-Host "`n[+] Checking Frontend Node Environment..." -ForegroundColor Yellow
Set-Location -Path "frontend"
if (-not (Test-Path -Path "node_modules")) {
    Write-Host "[+] Installing Frontend Node dependencies..." -ForegroundColor Yellow
    npm install
} else {
    Write-Host "[✓] Frontend node_modules exists." -ForegroundColor Green
}
Set-Location -Path ".."

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host " [✓] SmartMES Setup Completed Successfully!       " -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
