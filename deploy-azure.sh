#!/bin/bash

# Manual Azure App Service Deployment Script
# Run this if GitHub Actions deployment fails

echo "🚀 Starting manual deployment to Azure App Service..."

# Configuration
APP_NAME="rakk-ai"
RESOURCE_GROUP="rakkrag-rg"
LOCATION="Southeast Asia"

echo "📋 Configuration:"
echo "   App Name: $APP_NAME"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Location: $LOCATION"

# Check if logged in to Azure
echo "🔐 Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

echo "✅ Azure login verified"

# Create or verify resource group
echo "📁 Setting up resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION" --output table

# Create or verify app service plan
echo "📦 Setting up app service plan..."
if ! az appservice plan show --name "${APP_NAME}-plan" --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating new app service plan..."
    az appservice plan create \
        --name "${APP_NAME}-plan" \
        --resource-group $RESOURCE_GROUP \
        --sku B1 \
        --is-linux \
        --output table
else
    echo "✅ App service plan already exists"
fi

# Create or verify web app
echo "🌐 Setting up web app..."
if ! az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating new web app..."
    az webapp create \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --plan "${APP_NAME}-plan" \
        --runtime "PYTHON|3.12" \
        --output table
else
    echo "✅ Web app already exists"
fi

# Configure startup file
echo "⚙️ Configuring startup command..."
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind=0.0.0.0:8000" \
    --output table

# Deploy code using ZIP deployment
echo "📦 Preparing deployment package..."
zip -r deploy.zip . -x \
    "*.git*" \
    "__pycache__/*" \
    "test-env/*" \
    "venv/*" \
    ".pytest_cache/*" \
    "*.pyc" \
    "deploy.zip"

echo "🚀 Deploying to Azure..."
az webapp deployment source config-zip \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --src deploy.zip

# Clean up
rm deploy.zip

# Restart the app
echo "🔄 Restarting application..."
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

echo "✅ Deployment completed!"
echo "🌐 Your app should be available at: https://${APP_NAME}.azurewebsites.net"
echo "📊 Check health at: https://${APP_NAME}.azurewebsites.net/health"
echo "📚 API docs at: https://${APP_NAME}.azurewebsites.net/docs"

echo ""
echo "📋 To check deployment logs:"
echo "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
