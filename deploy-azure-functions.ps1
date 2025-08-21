# Manual Azure Functions Deployment Script (PowerShell)
# Run this if GitHub Actions deployment fails

Write-Host "🚀 Starting manual deployment to Azure Functions..." -ForegroundColor Green

# Configuration
$FUNCTION_APP_NAME = "rakk-ai"
$RESOURCE_GROUP = "rakkrag-rg"
$LOCATION = "East US"
$STORAGE_ACCOUNT = "rakkragstg$(Get-Random)"

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Function App: $FUNCTION_APP_NAME"
Write-Host "   Resource Group: $RESOURCE_GROUP"
Write-Host "   Location: $LOCATION"
Write-Host "   Storage Account: $STORAGE_ACCOUNT"

# Check if logged in to Azure
Write-Host "🔐 Checking Azure login..." -ForegroundColor Yellow
try {
    az account show | Out-Null
    Write-Host "✅ Azure login verified" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Azure. Please run: az login" -ForegroundColor Red
    exit 1
}

# Check if Azure Functions Core Tools is installed
Write-Host "🔧 Checking Azure Functions Core Tools..." -ForegroundColor Yellow
try {
    func --version | Out-Null
    Write-Host "✅ Azure Functions Core Tools found" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure Functions Core Tools not found." -ForegroundColor Red
    Write-Host "Please install it: npm install -g azure-functions-core-tools@4 --unsafe-perm true" -ForegroundColor Yellow
    exit 1
}

# Create or verify resource group
Write-Host "📁 Setting up resource group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION --output table

# Create storage account if it doesn't exist
Write-Host "💾 Setting up storage account..." -ForegroundColor Yellow
$storageExists = az storage account show --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP 2>$null
if (-not $storageExists) {
    Write-Host "Creating new storage account..." -ForegroundColor Yellow
    az storage account create `
        --name $STORAGE_ACCOUNT `
        --resource-group $RESOURCE_GROUP `
        --location $LOCATION `
        --sku Standard_LRS `
        --output table
} else {
    Write-Host "✅ Storage account already exists" -ForegroundColor Green
}

# Create Function App if it doesn't exist
Write-Host "⚡ Setting up Function App..." -ForegroundColor Yellow
$functionAppExists = az functionapp show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP 2>$null
if (-not $functionAppExists) {
    Write-Host "Creating new Function App..." -ForegroundColor Yellow
    az functionapp create `
        --resource-group $RESOURCE_GROUP `
        --consumption-plan-location $LOCATION `
        --runtime python `
        --runtime-version 3.12 `
        --functions-version 4 `
        --name $FUNCTION_APP_NAME `
        --storage-account $STORAGE_ACCOUNT `
        --os-type Linux `
        --output table
} else {
    Write-Host "✅ Function App already exists" -ForegroundColor Green
}

# Configure app settings if azure-settings.json exists
if (Test-Path "azure-settings.json") {
    Write-Host "⚙️ Configuring application settings..." -ForegroundColor Yellow
    az functionapp config appsettings set `
        --name $FUNCTION_APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --settings '@azure-settings.json'
} else {
    Write-Host "⚠️ azure-settings.json not found. Please configure environment variables manually." -ForegroundColor Yellow
}

# Deploy using Azure Functions Core Tools
Write-Host "🚀 Deploying to Azure Functions..." -ForegroundColor Yellow
Write-Host "Using simplified deployment approach..." -ForegroundColor Yellow
func azure functionapp publish $FUNCTION_APP_NAME --python --no-build

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Your Function App should be available at: https://$FUNCTION_APP_NAME.azurewebsites.net" -ForegroundColor Cyan
Write-Host "📊 Check health at: https://$FUNCTION_APP_NAME.azurewebsites.net/health" -ForegroundColor Cyan
Write-Host "📚 API docs at: https://$FUNCTION_APP_NAME.azurewebsites.net/docs" -ForegroundColor Cyan

Write-Host ""
Write-Host "📋 To check deployment logs:" -ForegroundColor Yellow
Write-Host "   az webapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP" -ForegroundColor White
Write-Host ""
Write-Host "📋 To manage functions:" -ForegroundColor Yellow
Write-Host "   az functionapp function list --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP" -ForegroundColor White
