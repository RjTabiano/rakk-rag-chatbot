#!/usr/bin/env powershell
"""
Manual Azure Functions Deployment Script
This script allows you to manually deploy to Azure Functions using the zip package method.
"""

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$FunctionAppName,
    
    [string]$PackagePath = "azure-functions-deployment.zip"
)

Write-Host "Azure Functions Manual Deployment Script" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Check if package exists
if (-not (Test-Path $PackagePath)) {
    Write-Host "Creating deployment package..." -ForegroundColor Yellow
    python create_deployment_package.py
    
    if (-not (Test-Path $PackagePath)) {
        Write-Host "Error: Could not create deployment package" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Package found: $PackagePath" -ForegroundColor Green

# Check if Azure CLI is installed
try {
    az --version | Out-Null
    Write-Host "Azure CLI found" -ForegroundColor Green
} catch {
    Write-Host "Error: Azure CLI not found. Please install Azure CLI first." -ForegroundColor Red
    exit 1
}

# Login check
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "Not logged in. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

# Deploy using zip deployment
Write-Host "Deploying to Azure Functions..." -ForegroundColor Yellow
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Cyan
Write-Host "Function App: $FunctionAppName" -ForegroundColor Cyan

try {
    # Deploy the zip package
    $result = az functionapp deployment source config-zip `
        --resource-group $ResourceGroupName `
        --name $FunctionAppName `
        --src $PackagePath `
        --build-remote true `
        --output json | ConvertFrom-Json
    
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
    Write-Host "Deployment URL: $($result.complete_url)" -ForegroundColor Cyan
    
    # Get the function app URL
    $appInfo = az functionapp show --resource-group $ResourceGroupName --name $FunctionAppName --output json | ConvertFrom-Json
    $appUrl = "https://$($appInfo.defaultHostName)"
    
    Write-Host "Function App URL: $appUrl" -ForegroundColor Green
    Write-Host "Health Check: $appUrl/health" -ForegroundColor Cyan
    Write-Host "Test Endpoint: $appUrl/test" -ForegroundColor Cyan
    
} catch {
    Write-Host "Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`nDeployment complete! 🎉" -ForegroundColor Green
