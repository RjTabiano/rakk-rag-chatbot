# Azure Deployment Configuration for RakkA.I(RAG)

## Important: App Service vs Azure Functions

This application is configured for **Azure App Service** (web app), NOT Azure Functions. 
If you created an Azure Functions app, you need to create an Azure App Service instead.

## Environment Variables Required for Azure
# Set these in Azure App Service Configuration > Application Settings

GOOGLE_API_KEY=your-google-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=your-pinecone-index-name
RAG_NAMESPACE=your-rag-namespace

# Database Configuration
DB_HOST=your-azure-mysql-host
DB_PORT=3306
DB_DATABASE=your-database-name
DB_USERNAME=your-db-username
DB_PASSWORD=your-db-password

# Azure-specific settings
PORT=8000
HOST=0.0.0.0
WEBSITE_HOSTNAME=your-app-name.azurewebsites.net

## Azure CLI Commands for Deployment

# 1. Create Resource Group
az group create --name rakkrag-rg --location "East US"

# 2. Create App Service Plan (Linux)
az appservice plan create --name rakkrag-plan --resource-group rakkrag-rg --sku B1 --is-linux

# 3. Create Web App (NOT Function App!)
az webapp create --resource-group rakkrag-rg --plan rakkrag-plan --name rakk-ai --runtime "PYTHON|3.12"

# 4. Configure startup command
az webapp config set --resource-group rakkrag-rg --name rakk-ai --startup-file "startup.py"

# 5. Configure App Settings
az webapp config appsettings set --resource-group rakkrag-rg --name rakk-ai --settings @azure-settings.json

# 6. Enable logging
az webapp log config --resource-group rakkrag-rg --name rakk-ai --application-logging true --level information

# 7. Deploy code using GitHub Actions (recommended) or local Git
# For GitHub Actions: Push to azure-deployment branch
# For local Git:
az webapp deployment source config-local-git --name rakk-ai --resource-group rakkrag-rg
git remote add azure <deployment-url>
git push azure azure-deployment:master

## Troubleshooting Common Issues

### 1. Function App vs App Service Error
If you see "sync trigger" errors, you likely created an Azure Functions app instead of an App Service.
**Solution**: Delete the Function App and create an App Service instead using the commands above.

### 2. Startup Issues
Check the application logs:
```bash
az webapp log tail --resource-group rakkrag-rg --name rakk-ai
```

### 3. Import Path Issues
The application automatically configures Python paths for Azure. If you see import errors:
- Ensure `startup.py` is in the root directory
- Check that `app/` directory structure is maintained
- Verify environment variable `PYTHONPATH` is set to `.` or `/home/site/wwwroot`
