# Azure Deployment Configuration for RakkA.I(RAG)

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

# 2. Create App Service Plan
az appservice plan create --name rakkrag-plan --resource-group rakkrag-rg --sku B1 --is-linux

# 3. Create Web App
az webapp create --resource-group rakkrag-rg --plan rakkrag-plan --name rakkrag-chatbot --runtime "PYTHON|3.12"

# 4. Configure App Settings
az webapp config appsettings set --resource-group rakkrag-rg --name rakkrag-chatbot --settings @azure-settings.json

# 5. Configure startup command
az webapp config set --resource-group rakkrag-rg --name rakkrag-chatbot --startup-file "startup.py"

# 6. Enable logging
az webapp log config --resource-group rakkrag-rg --name rakkrag-chatbot --application-logging true --level information

# 7. Deploy code
az webapp deployment source config-local-git --name rakkrag-chatbot --resource-group rakkrag-rg
git remote add azure <deployment-url>
git push azure azure-deployment:master
