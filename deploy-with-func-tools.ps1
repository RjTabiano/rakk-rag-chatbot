#!/usr/bin/env powershell
<#
.SYNOPSIS
    Deploy to Azure Functions using Azure Functions Core Tools
.DESCRIPTION
    This script uses func CLI to deploy directly to Azure Functions, bypassing GitHub Actions issues
.PARAMETER FunctionAppName
    The name of the Azure Function App
.PARAMETER ResourceGroupName
    The Azure Resource Group containing the Function App
.PARAMETER SubscriptionId
    Azure Subscription ID (optional, uses current subscription if not specified)
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$FunctionAppName,
    
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [string]$SubscriptionId
)

Write-Host "Azure Functions Core Tools Deployment" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if Azure Functions Core Tools is installed
Write-Host "Checking Azure Functions Core Tools..." -ForegroundColor Yellow
try {
    $funcVersion = func --version
    Write-Host "✓ Azure Functions Core Tools found: $funcVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Azure Functions Core Tools not found." -ForegroundColor Red
    Write-Host "Please install from: https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local" -ForegroundColor Yellow
    Write-Host "Or run: npm install -g azure-functions-core-tools@4 --unsafe-perm true" -ForegroundColor Yellow
    exit 1
}

# Check Azure CLI
Write-Host "Checking Azure CLI..." -ForegroundColor Yellow
try {
    $azVersion = az --version | Select-String "azure-cli" | Select-Object -First 1
    Write-Host "✓ Azure CLI found: $azVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Azure CLI not found. Please install Azure CLI first." -ForegroundColor Red
    exit 1
}

# Check login status
Write-Host "Checking Azure authentication..." -ForegroundColor Yellow
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "✓ Logged in as: $($account.user.name)" -ForegroundColor Green
    Write-Host "✓ Subscription: $($account.name) ($($account.id))" -ForegroundColor Green
    
    if ($SubscriptionId -and $account.id -ne $SubscriptionId) {
        Write-Host "Setting subscription to: $SubscriptionId" -ForegroundColor Yellow
        az account set --subscription $SubscriptionId
    }
} catch {
    Write-Host "✗ Not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

# Verify function app exists
Write-Host "Verifying Function App exists..." -ForegroundColor Yellow
try {
    $functionApp = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
    Write-Host "✓ Function App found: $($functionApp.name)" -ForegroundColor Green
    Write-Host "✓ URL: https://$($functionApp.defaultHostName)" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Function App '$FunctionAppName' not found in resource group '$ResourceGroupName'" -ForegroundColor Red
    exit 1
}

# Create a clean build directory
Write-Host "Preparing deployment package..." -ForegroundColor Yellow
$buildDir = ".\build-deploy"
if (Test-Path $buildDir) {
    Remove-Item $buildDir -Recurse -Force
}
New-Item -ItemType Directory -Path $buildDir | Out-Null

# Copy essential files only
$filesToCopy = @(
    "function_app.py",
    "main.py", 
    "host.json",
    "requirements.txt"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item $file $buildDir
        Write-Host "✓ Copied: $file" -ForegroundColor Green
    } else {
        Write-Host "⚠ Missing: $file" -ForegroundColor Yellow
    }
}

# Copy optional files
$optionalFiles = @(
    "function.json",
    "local.settings.json",
    ".funcignore"
)

foreach ($file in $optionalFiles) {
    if (Test-Path $file) {
        Copy-Item $file $buildDir
        Write-Host "✓ Copied: $file" -ForegroundColor Green
    }
}

# Copy app directory
if (Test-Path "app") {
    Copy-Item "app" $buildDir -Recurse
    Write-Host "✓ Copied: app/ directory" -ForegroundColor Green
} else {
    Write-Host "⚠ Missing: app/ directory" -ForegroundColor Yellow
}

# Change to build directory
Push-Location $buildDir

try {
    # Initialize if needed (this creates .vscode/settings.json if it doesn't exist)
    if (-not (Test-Path ".vscode")) {
        Write-Host "Initializing Functions project..." -ForegroundColor Yellow
        func init --python --name $FunctionAppName
    }

    # Deploy using func CLI
    Write-Host "Deploying to Azure Functions..." -ForegroundColor Yellow
    Write-Host "Target: $FunctionAppName" -ForegroundColor Cyan
    
    func azure functionapp publish $FunctionAppName --python
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Deployment successful!" -ForegroundColor Green
        
        # Test the deployment
        $appUrl = "https://$($functionApp.defaultHostName)"
        Write-Host "`nDeployment complete! 🎉" -ForegroundColor Green
        Write-Host "Function App URL: $appUrl" -ForegroundColor Cyan
        Write-Host "Health Check: $appUrl/health" -ForegroundColor Cyan
        Write-Host "Test Endpoint: $appUrl/test" -ForegroundColor Cyan
        
        # Test health endpoint
        Write-Host "`nTesting health endpoint..." -ForegroundColor Yellow
        try {
            $response = Invoke-RestMethod -Uri "$appUrl/health" -Method GET -TimeoutSec 30
            Write-Host "✓ Health check successful: $($response)" -ForegroundColor Green
        } catch {
            Write-Host "⚠ Health check failed: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host "This may be normal if the app is still starting up." -ForegroundColor Gray
        }
        
    } else {
        Write-Host "✗ Deployment failed!" -ForegroundColor Red
        exit 1
    }
    
} finally {
    # Return to original directory
    Pop-Location
    
    # Clean up build directory
    if (Test-Path $buildDir) {
        Remove-Item $buildDir -Recurse -Force
        Write-Host "✓ Cleaned up build directory" -ForegroundColor Green
    }
}

Write-Host "`n🚀 Deployment completed successfully!" -ForegroundColor Green
