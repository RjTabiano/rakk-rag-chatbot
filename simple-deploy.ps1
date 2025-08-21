#!/usr/bin/env powershell
<#
.SYNOPSIS
    Simple Azure Functions deployment using Azure CLI zip deploy
.DESCRIPTION
    Creates a minimal, clean zip package and deploys it using Azure CLI
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$FunctionAppName,
    
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName
)

Write-Host "Simple Azure Functions Deployment" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Create minimal deployment package
Write-Host "Creating minimal deployment package..." -ForegroundColor Yellow

$deployDir = ".\minimal-deploy"
if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copy only essential files
Copy-Item "function_app.py" $deployDir
Copy-Item "main.py" $deployDir 
Copy-Item "host.json" $deployDir
Copy-Item "requirements.txt" $deployDir

# Copy app directory
Copy-Item "app" $deployDir -Recurse

Write-Host "✓ Essential files copied" -ForegroundColor Green

# Create zip package
$zipPath = ".\minimal-azure-functions.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

# Use PowerShell to create zip
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($deployDir, $zipPath)

Write-Host "✓ Created zip package: $zipPath" -ForegroundColor Green

# Get zip file size
$zipSize = (Get-Item $zipPath).Length / 1MB
Write-Host "✓ Package size: $($zipSize.ToString('F2')) MB" -ForegroundColor Green

# List zip contents
Write-Host "`nPackage contents:" -ForegroundColor Cyan
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
$zip.Entries | ForEach-Object { Write-Host "  $($_.FullName)" -ForegroundColor Gray }
$zip.Dispose()

# Deploy using Azure CLI
Write-Host "`nDeploying to Azure..." -ForegroundColor Yellow
try {
    az functionapp deployment source config-zip `
        --resource-group $ResourceGroupName `
        --name $FunctionAppName `
        --src $zipPath `
        --build-remote
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Deployment successful!" -ForegroundColor Green
        
        # Get function app URL
        $appInfo = az functionapp show --resource-group $ResourceGroupName --name $FunctionAppName --output json | ConvertFrom-Json
        $appUrl = "https://$($appInfo.defaultHostName)"
        
        Write-Host "`nDeployment complete! 🎉" -ForegroundColor Green
        Write-Host "Function App URL: $appUrl" -ForegroundColor Cyan
        Write-Host "Health Check: $appUrl/health" -ForegroundColor Cyan
        Write-Host "Test Endpoint: $appUrl/test" -ForegroundColor Cyan
    } else {
        Write-Host "✗ Deployment failed!" -ForegroundColor Red
    }
    
} catch {
    Write-Host "✗ Deployment error: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Cleanup
    if (Test-Path $deployDir) {
        Remove-Item $deployDir -Recurse -Force
    }
}

Write-Host "`nDone!" -ForegroundColor Green
