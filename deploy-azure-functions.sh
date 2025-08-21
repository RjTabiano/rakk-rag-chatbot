#!/bin/bash

# Manual Azure Functions Deployment Script
# Run this if GitHub Actions deployment fails

echo "🚀 Starting manual deployment to Azure Functions..."

# Configuration
FUNCTION_APP_NAME="rakk-ai"
RESOURCE_GROUP="rakkrag-rg"
LOCATION="East US"
STORAGE_ACCOUNT="rakkragstg$(date +%s)"

echo "📋 Configuration:"
echo "   Function App: $FUNCTION_APP_NAME"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Location: $LOCATION"
echo "   Storage Account: $STORAGE_ACCOUNT"

# Check if logged in to Azure
echo "🔐 Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

echo "✅ Azure login verified"

# Check if Azure Functions Core Tools is installed
echo "🔧 Checking Azure Functions Core Tools..."
if ! command -v func &> /dev/null; then
    echo "❌ Azure Functions Core Tools not found."
    echo "Please install it: npm install -g azure-functions-core-tools@4 --unsafe-perm true"
    exit 1
fi

echo "✅ Azure Functions Core Tools found"

# Create or verify resource group
echo "📁 Setting up resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION" --output table

# Create storage account if it doesn't exist
echo "💾 Setting up storage account..."
if ! az storage account show --name $STORAGE_ACCOUNT --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating new storage account..."
    az storage account create \
        --name $STORAGE_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --location "$LOCATION" \
        --sku Standard_LRS \
        --output table
else
    echo "✅ Storage account already exists"
fi

# Create Function App if it doesn't exist
echo "⚡ Setting up Function App..."
if ! az functionapp show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating new Function App..."
    az functionapp create \
        --resource-group $RESOURCE_GROUP \
        --consumption-plan-location "$LOCATION" \
        --runtime python \
        --runtime-version 3.12 \
        --functions-version 4 \
        --name $FUNCTION_APP_NAME \
        --storage-account $STORAGE_ACCOUNT \
        --os-type Linux \
        --output table
else
    echo "✅ Function App already exists"
fi

# Configure app settings if azure-settings.json exists
if [ -f "azure-settings.json" ]; then
    echo "⚙️ Configuring application settings..."
    az functionapp config appsettings set \
        --name $FUNCTION_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --settings @azure-settings.json
else
    echo "⚠️ azure-settings.json not found. Please configure environment variables manually."
fi

# Deploy using Azure Functions Core Tools
echo "🚀 Deploying to Azure Functions..."
echo "Using simplified deployment approach..."
func azure functionapp publish $FUNCTION_APP_NAME --python --no-build

echo "✅ Deployment completed!"
echo "🌐 Your Function App should be available at: https://${FUNCTION_APP_NAME}.azurewebsites.net"
echo "📊 Check health at: https://${FUNCTION_APP_NAME}.azurewebsites.net/health"
echo "📚 API docs at: https://${FUNCTION_APP_NAME}.azurewebsites.net/docs"

echo ""
echo "📋 To check deployment logs:"
echo "   az webapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "📋 To manage functions:"
echo "   az functionapp function list --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP"
