param (
    [string]$LambdaName
)

if (-not $LambdaName) {
    Write-Error "LambdaName parameter is required."
    exit 1
}

$sourcePath = "src/tools/$LambdaName"
$requirementsPath = Join-Path $sourcePath "requirements.txt"
$packagePath = Join-Path $sourcePath "package"

if (Test-Path $requirementsPath) {
    Write-Host "Installing dependencies for $LambdaName..."
    # Create a temporary directory for dependencies
    if (Test-Path $packagePath) {
        Remove-Item -Recurse -Force $packagePath
    }
    New-Item -ItemType Directory -Path $packagePath | Out-Null
    
    # Install dependencies into the package directory
    pip install --target $packagePath -r $requirementsPath
} else {
    Write-Host "No requirements.txt found for $LambdaName. Skipping dependency installation."
}
