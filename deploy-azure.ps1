# Manual Azure App Service Deployment Script (PowerShell)
# Run this if GitHub Actions deployment fails

Write-Host "🚀 Starting manual deployment to Azure App Service..." -ForegroundColor Green

# Configuration
$APP_NAME = "rakk-ai"
$RESOURCE_GROUP = "rakkrag-rg"
$LOCATION = "Southeast Asia"

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   App Name: $APP_NAME"
Write-Host "   Resource Group: $RESOURCE_GROUP"
Write-Host "   Location: $LOCATION"

# Check if logged in to Azure
Write-Host "🔐 Checking Azure login..." -ForegroundColor Yellow
try {
    az account show | Out-Null
    Write-Host "✅ Azure login verified" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Azure. Please run: az login" -ForegroundColor Red
    exit 1
}

# Create or verify resource group
Write-Host "📁 Setting up resource group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION --output table

# Create or verify app service plan
Write-Host "📦 Setting up app service plan..." -ForegroundColor Yellow
$planExists = az appservice plan show --name "$APP_NAME-plan" --resource-group $RESOURCE_GROUP 2>$null
if (-not $planExists) {
    Write-Host "Creating new app service plan..." -ForegroundColor Yellow
    az appservice plan create `
        --name "$APP_NAME-plan" `
        --resource-group $RESOURCE_GROUP `
        --sku B1 `
        --is-linux `
        --output table
} else {
    Write-Host "✅ App service plan already exists" -ForegroundColor Green
}

# Create or verify web app
Write-Host "🌐 Setting up web app..." -ForegroundColor Yellow
$appExists = az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP 2>$null
if (-not $appExists) {
    Write-Host "Creating new web app..." -ForegroundColor Yellow
    az webapp create `
        --name $APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --plan "$APP_NAME-plan" `
        --runtime "PYTHON|3.12" `
        --output table
} else {
    Write-Host "✅ Web app already exists" -ForegroundColor Green
}

# Configure startup file
Write-Host "⚙️ Configuring startup command..." -ForegroundColor Yellow
az webapp config set `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --startup-file "gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind=0.0.0.0:8000" `
    --output table

# Deploy code using ZIP deployment
Write-Host "📦 Preparing deployment package..." -ForegroundColor Yellow

# Create a temporary directory for clean files
$tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
$deployZip = "deploy.zip"

# Copy files excluding unnecessary ones
$excludePatterns = @("*.git*", "__pycache__", "test-env", "venv", ".pytest_cache", "*.pyc")
Get-ChildItem -Path . -Recurse | Where-Object {
    $item = $_
    -not ($excludePatterns | Where-Object { $item.FullName -like "*$_*" })
} | Copy-Item -Destination { Join-Path $tempDir.FullName $_.FullName.Substring((Get-Location).Path.Length) } -Force

# Create ZIP file
Compress-Archive -Path "$tempDir\*" -DestinationPath $deployZip -Force
Remove-Item $tempDir -Recurse -Force

Write-Host "🚀 Deploying to Azure..." -ForegroundColor Yellow
az webapp deployment source config-zip `
    --name $APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --src $deployZip

# Clean up
Remove-Item $deployZip -Force

# Restart the app
Write-Host "🔄 Restarting application..." -ForegroundColor Yellow
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Your app should be available at: https://$APP_NAME.azurewebsites.net" -ForegroundColor Cyan
Write-Host "📊 Check health at: https://$APP_NAME.azurewebsites.net/health" -ForegroundColor Cyan
Write-Host "📚 API docs at: https://$APP_NAME.azurewebsites.net/docs" -ForegroundColor Cyan

Write-Host ""
Write-Host "📋 To check deployment logs:" -ForegroundColor Yellow
Write-Host "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP" -ForegroundColor White
