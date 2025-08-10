param (
    [string]$LambdaName,
    [string]$Type = "agents"  # Default to agents, can be "agents" or "tools"
)

if (-not $LambdaName) {
    Write-Error "LambdaName parameter is required."
    Write-Host "Usage: .\build_lambdas.ps1 -LambdaName <name> [-Type <agents|tools>]"
    Write-Host "Examples:"
    Write-Host "  .\build_lambdas.ps1 -LambdaName agent_elevator -Type agents"
    Write-Host "  .\build_lambdas.ps1 -LambdaName tool_psim -Type tools"
    exit 1
}

# Determine source path based on type
if ($Type -eq "agents") {
    $sourcePath = "src/agents/$LambdaName"
} else {
    $sourcePath = "src/tools/$LambdaName"
}

$requirementsPath = Join-Path $sourcePath "requirements.txt"

Write-Host "🔧 Preparing Lambda dependencies: $LambdaName"
Write-Host "📁 Source path: $sourcePath"
Write-Host "🏷️  Type: $Type"
Write-Host ""

# Check if source directory exists
if (-not (Test-Path $sourcePath)) {
    Write-Error "Source path does not exist: $sourcePath"
    exit 1
}

# Install dependencies if requirements.txt exists
if (Test-Path $requirementsPath) {
    Write-Host "📦 Installing Python dependencies..."
    
    # Install dependencies directly in the source directory
    # Terraform will handle the ZIP creation with these dependencies
    pip install --target $sourcePath -r $requirementsPath --upgrade
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Failed to install dependencies"
        exit 1
    }
    
    Write-Host "✅ Dependencies installed successfully in source directory"
} else {
    Write-Host "ℹ️  No requirements.txt found for $LambdaName. Skipping dependency installation."
}

Write-Host ""
Write-Host "🎯 Next Steps for Deployment:"
Write-Host "1. Dependencies are ready in: $sourcePath"
Write-Host "2. Deploy using Terraform (recommended):"
Write-Host "   cd terraform/environments/dev"
Write-Host "   terraform plan"
Write-Host "   terraform apply"
Write-Host ""
Write-Host "💡 Terraform will automatically:"
Write-Host "   - Detect code changes"  
Write-Host "   - Create deployment ZIP"
Write-Host "   - Update Lambda function"
Write-Host "   - Maintain Infrastructure as Code consistency"

Write-Host ""
Write-Host "🚀 Dependencies prepared for $LambdaName - Ready for Terraform!"
