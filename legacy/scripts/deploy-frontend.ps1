# Deploy Frontend to S3/CloudFront
param(
    [string]$Environment = "dev",
    [string]$AwsProfile = "default"
)

Write-Host "🚀 Deploying BuildingOS Frontend to S3/CloudFront..." -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Yellow

# Configuration based on environment
$config = switch ($Environment) {
    "dev" {
        @{
            S3Bucket = "buildingos-frontend-dev"
            CloudFrontId = "E1234567890DEV"  # Replace with actual dev distribution ID
            Domain = "buildingos-dev.yourdomain.com"
            WebSocketEndpoint = "wss://websocket-api-dev.buildingos.com"
            ApiEndpoint = "https://api-dev.buildingos.com"
        }
    }
    "staging" {
        @{
            S3Bucket = "buildingos-frontend-staging"
            CloudFrontId = "E1234567890STAGING"  # Replace with actual staging distribution ID
            Domain = "buildingos-staging.yourdomain.com"
            WebSocketEndpoint = "wss://websocket-api-staging.buildingos.com"
            ApiEndpoint = "https://api-staging.buildingos.com"
        }
    }
    "prod" {
        @{
            S3Bucket = "buildingos-frontend-prod"
            CloudFrontId = "E1234567890PROD"  # Replace with actual prod distribution ID
            Domain = "buildingos.com"
            WebSocketEndpoint = "wss://websocket-api.buildingos.com"
            ApiEndpoint = "https://api.buildingos.com"
        }
    }
    default {
        Write-Host "❌ Invalid environment: $Environment" -ForegroundColor Red
        Write-Host "Valid environments: dev, staging, prod" -ForegroundColor Yellow
        exit 1
    }
}

# Check if AWS CLI is available
if (-not (Get-Command "aws" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI." -ForegroundColor Red
    exit 1
}

# Check AWS credentials
Write-Host "🔐 Checking AWS credentials..." -ForegroundColor Yellow
aws sts get-caller-identity --profile $AwsProfile | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ AWS credentials not configured for profile: $AwsProfile" -ForegroundColor Red
    Write-Host "Run: aws configure --profile $AwsProfile" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ AWS credentials verified" -ForegroundColor Green

# Create temporary directory for processed files
$tempDir = New-Item -ItemType Directory -Path (Join-Path $env:TEMP "buildingos-frontend-$(Get-Date -Format 'yyyyMMdd-HHmmss')") -Force
Write-Host "📁 Using temporary directory: $($tempDir.FullName)" -ForegroundColor Yellow

try {
    # Copy frontend files to temp directory
    Write-Host "📋 Copying frontend files..." -ForegroundColor Yellow
    Copy-Item -Path ".\frontend\*" -Destination $tempDir.FullName -Recurse -Force

    # Update configuration in files
    Write-Host "⚙️ Updating environment configuration..." -ForegroundColor Yellow
    
    # Create config.js file
    $configJs = @"
// Auto-generated configuration for environment: $Environment
const CONFIG = {
    development: {
        websocketEndpoint: 'ws://localhost:3001',
        apiEndpoint: 'http://localhost:3000',
        debug: true
    },
    staging: {
        websocketEndpoint: '$($config.WebSocketEndpoint)',
        apiEndpoint: '$($config.ApiEndpoint)',
        debug: true
    },
    production: {
        websocketEndpoint: '$($config.WebSocketEndpoint)',
        apiEndpoint: '$($config.ApiEndpoint)',
        debug: false
    }
};

// Auto-detect environment
function getEnvironment() {
    const hostname = window.location.hostname;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'development';
    } else if (hostname.includes('-dev.') || hostname.includes('dev-') || hostname.includes('-staging.') || hostname.includes('staging-')) {
        return 'staging';
    } else {
        return 'production';
    }
}

// Get current config
const CURRENT_ENV = getEnvironment();
const APP_CONFIG = CONFIG[CURRENT_ENV];

console.log(`🌍 Environment: `${CURRENT_ENV}`);
console.log(`🔗 WebSocket: `${APP_CONFIG.websocketEndpoint}`);
console.log(`🌐 API: `${APP_CONFIG.apiEndpoint}`);
"@

    $configJs | Out-File -FilePath (Join-Path $tempDir.FullName "config.js") -Encoding UTF8

    # Update HTML files to include config.js
    $htmlFiles = Get-ChildItem -Path $tempDir.FullName -Filter "*.html"
    foreach ($htmlFile in $htmlFiles) {
        $content = Get-Content -Path $htmlFile.FullName -Raw
        
        # Add config.js script tag before closing </head>
        $content = $content -replace '</head>', "    <script src=`"config.js`"></script>`n</head>"
        
        # Update WebSocket endpoint references to use APP_CONFIG
        $content = $content -replace "websocketEndpoint: 'wss://websocket-api\.buildingos\.dev'", "websocketEndpoint: APP_CONFIG.websocketEndpoint"
        $content = $content -replace "apiEndpoint: 'https://pj4vlvxrg7\.execute-api\.us-east-1\.amazonaws\.com'", "apiEndpoint: APP_CONFIG.apiEndpoint"
        
        $content | Out-File -FilePath $htmlFile.FullName -Encoding UTF8
    }

    # Check if S3 bucket exists
    Write-Host "🪣 Checking S3 bucket: $($config.S3Bucket)" -ForegroundColor Yellow
    $bucketCheck = aws s3 ls "s3://$($config.S3Bucket)" --profile $Profile 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ S3 bucket not found: $($config.S3Bucket)" -ForegroundColor Red
        Write-Host "Please create the bucket first or check the bucket name" -ForegroundColor Yellow
        exit 1
    }

    # Sync files to S3
    Write-Host "📦 Uploading files to S3 bucket: $($config.S3Bucket)" -ForegroundColor Yellow
    
    # Upload with cache control for static assets
    aws s3 sync $tempDir.FullName "s3://$($config.S3Bucket)/" `
        --delete `
        --exclude "*.md" `
        --exclude ".git*" `
        --exclude "*.tmp" `
        --cache-control "public, max-age=31536000" `
        --profile $Profile

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ S3 sync failed" -ForegroundColor Red
        exit 1
    }

    # Set specific cache control for HTML files (shorter cache)
    Write-Host "⚙️ Setting cache control for HTML files..." -ForegroundColor Yellow
    
    $htmlFiles = @("index.html", "chat-websocket-pure.html", "chat-new-architecture.html", "chat-with-notifications.html")
    foreach ($htmlFile in $htmlFiles) {
        aws s3 cp "s3://$($config.S3Bucket)/$htmlFile" "s3://$($config.S3Bucket)/$htmlFile" `
            --metadata-directive REPLACE `
            --cache-control "public, max-age=300" `
            --content-type "text/html" `
            --profile $Profile `
            2>$null
    }

    # Set cache control for config.js (short cache for dynamic config)
    aws s3 cp "s3://$($config.S3Bucket)/config.js" "s3://$($config.S3Bucket)/config.js" `
        --metadata-directive REPLACE `
        --cache-control "public, max-age=300" `
        --content-type "application/javascript" `
        --profile $Profile

    Write-Host "✅ Files uploaded to S3 successfully" -ForegroundColor Green

    # Invalidate CloudFront cache
    Write-Host "🔄 Invalidating CloudFront cache..." -ForegroundColor Yellow
    
    $invalidationResult = aws cloudfront create-invalidation `
        --distribution-id $config.CloudFrontId `
        --paths "/*" `
        --profile $Profile `
        --output json 2>&1

    if ($LASTEXITCODE -eq 0) {
        $invalidation = $invalidationResult | ConvertFrom-Json
        Write-Host "✅ CloudFront invalidation created: $($invalidation.Invalidation.Id)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ CloudFront invalidation failed, but deployment succeeded" -ForegroundColor Yellow
        Write-Host "You may need to wait for cache expiration or manually invalidate" -ForegroundColor Yellow
    }

    # Success summary
    Write-Host ""
    Write-Host "🎉 Frontend deployed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 Deployment Summary:" -ForegroundColor Cyan
    Write-Host "  • Environment: $Environment" -ForegroundColor White
    Write-Host "  • S3 Bucket: $($config.S3Bucket)" -ForegroundColor White
    Write-Host "  • CloudFront: $($config.CloudFrontId)" -ForegroundColor White
    Write-Host "  • Domain: https://$($config.Domain)" -ForegroundColor White
    Write-Host "  • WebSocket: $($config.WebSocketEndpoint)" -ForegroundColor White
    Write-Host "  • API: $($config.ApiEndpoint)" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 URLs:" -ForegroundColor Cyan
    Write-Host "  • Main: https://$($config.Domain)" -ForegroundColor Cyan
    Write-Host "  • WebSocket Chat: https://$($config.Domain)/chat-websocket-pure.html" -ForegroundColor Cyan
    Write-Host "  • SNS Architecture: https://$($config.Domain)/chat-new-architecture.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⏱️ Cache invalidation may take 10-15 minutes to propagate" -ForegroundColor Yellow

} finally {
    # Cleanup temporary directory
    Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Yellow
    Remove-Item -Path $tempDir.FullName -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "✅ Deployment completed!" -ForegroundColor Green
