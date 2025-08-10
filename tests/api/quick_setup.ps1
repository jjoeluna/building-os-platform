# Quick Setup Script for BuildingOS API Testing
# Usage: .\tests\api\quick_setup.ps1

Write-Host "🚀 BuildingOS API Testing Quick Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if we're in the right directory
$currentDir = Get-Location
if (-not $currentDir.Path.EndsWith("building-os-platform")) {
    Write-Host "❌ Please run this script from the building-os-platform root directory" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    & .\.venv\Scripts\Activate.ps1
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not found. Please run setup first." -ForegroundColor Red
    exit 1
}

# Navigate to test directory
Write-Host "📁 Navigating to tests directory..." -ForegroundColor Yellow
Set-Location "tests\api"

# Check dependencies
Write-Host "🔍 Checking test dependencies..." -ForegroundColor Yellow
try {
    python -c "import pytest, requests, rich; print('All dependencies available')"
    Write-Host "✅ All test dependencies are available" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Show available commands
Write-Host ""
Write-Host "🛠️  Available Commands:" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 Quick Diagnosis (30s):" -ForegroundColor Yellow
Write-Host "   python diagnose_api.py" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Complete Test Suite:" -ForegroundColor Yellow  
Write-Host "   python run_tests.py" -ForegroundColor White
Write-Host ""
Write-Host "⚡ Specific Endpoint Tests:" -ForegroundColor Yellow
Write-Host "   python -m pytest test_endpoints.py::TestElevatorEndpoint -v" -ForegroundColor White
Write-Host "   python -m pytest test_endpoints.py::TestPersonaEndpoint -v" -ForegroundColor White
Write-Host "   python -m pytest test_endpoints.py::TestCORSHeaders -v" -ForegroundColor White
Write-Host ""
Write-Host "📊 View Recent Results:" -ForegroundColor Green
Write-Host "   Get-ChildItem api-test-results-*.json | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content | ConvertFrom-Json | Select-Object -ExpandProperty summary" -ForegroundColor White

Write-Host "`n🎯 Ready for development! Use the commands above for testing." -ForegroundColor Cyan
