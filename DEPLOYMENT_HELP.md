# Manual Deployment Steps

If GitHub Actions deployment is not working, try manual deployment:

## Method 1: Using Azure CLI (Recommended)
```bash
# Install Azure CLI if not already installed
# Then login
az login

# Deploy the function app
az functionapp deployment source config-zip --resource-group your-resource-group --name rakk-rag-chatbot --src deployment.zip
```

## Method 2: Using func command
```bash
# Make sure you're in the project directory
func azure functionapp publish rakk-rag-chatbot
```

## Method 3: Check Current Status
Visit your GitHub Actions to see if deployment succeeded:
https://github.com/RjTabiano/rakk-rag-chatbot/actions
