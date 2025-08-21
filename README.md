# RakkA.I(RAG) Project

## Overview
RakkA.I(RAG) is a FastAPI application designed to leverage Langchain functionalities for various AI-driven tasks. This project provides a structured approach to building and deploying AI applications with a focus on modularity and scalability.

## Requirements
- Python 3.12 or higher
- pip (Python package installer)
- Access to Google AI API and Pinecone for vector storage
- MySQL database for product information

## Project Structure
```
RakkA.I(RAG)
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── chat.py
│   │   └── ingest.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── prompts.py
│   ├── models/
│   │   ├── chat.py
│   │   └── ingest.py
│   ├── services/
│   │   ├── ingest_service.py
│   │   ├── pinecone_service.py
│   │   ├── product_service.py
│   │   └── rag_service.py
│   └── utils/
│       ├── chunking.py
│       ├── db_connection.py
│       ├── formatter.py
│       ├── pdf_loader.py
│       └── rag_utils.py
├── data/
├── .env
├── .python-version           # Python version specification
├── requirements.txt
└── README.md
```

## Installation

### Local Development
To get started with the RakkA.I(RAG) project, follow these steps:

1. **Prerequisites**: Ensure you have Python 3.12 installed on your system.
   ```bash
   python --version  # Should show Python 3.12.x
   ```

2. Clone the repository:
   ```bash
   git clone <repository-url>
   cd RakkA.I(RAG)
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables
Create a `.env` file in the root directory and define the following environment variables:

```env
# Google AI API
GOOGLE_API_KEY=your-google-api-key

# Pinecone Vector Database
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=your-pinecone-index-name
RAG_NAMESPACE=your-rag-namespace

# MySQL Database Configuration
DB_HOST=your-db-host
DB_PORT=your-db-port
DB_DATABASE=your-database-name
DB_USERNAME=your-db-username
DB_PASSWORD=your-db-password
```

## Usage

### Local Development
To run the application locally, make sure your virtual environment is activated and execute:

```bash
# Activate virtual environment (if not already active)
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

# Start the development server
uvicorn app.main:app --reload
```

The application will be available at:
- **API**: `http://127.0.0.1:8000`
- **Interactive API Documentation**: `http://127.0.0.1:8000/docs`
- **Alternative API Documentation**: `http://127.0.0.1:8000/redoc`

## Azure Functions Deployment

This project is configured for deployment on Azure Functions with Python 3.12 runtime using the ASGI integration pattern.

### Prerequisites for Azure Functions Deployment
1. Azure CLI installed and configured
2. Azure Functions Core Tools installed
3. Azure subscription with appropriate permissions
4. Resource group created for the application

### Azure Functions Deployment Steps

1. **Install Azure Functions Core Tools**:
   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Create Azure Function App**:
   ```bash
   # Create resource group (if not exists)
   az group create --name rakkrag-rg --location "East US"
   
   # Create storage account (required for Functions)
   az storage account create --name rakkragstg$(date +%s) --resource-group rakkrag-rg --location "East US" --sku Standard_LRS
   
   # Create Function App
   az functionapp create --resource-group rakkrag-rg --consumption-plan-location "East US" --runtime python --runtime-version 3.12 --functions-version 4 --name rakk-ai --storage-account rakkragstg$(date +%s) --os-type Linux
   ```

3. **Configure Environment Variables**:
   ```bash
   az functionapp config appsettings set --name rakk-ai --resource-group rakkrag-rg --settings @azure-settings.json
   ```

4. **Deploy the Application**:
   ```bash
   # Deploy using GitHub Actions (recommended) or manual deployment
   # For GitHub Actions: Push to azure-deployment branch
   # For manual deployment:
   func azure functionapp publish rakk-ai --python
   ```

### Alternative Deployment Methods

#### Manual Deployment Scripts
```bash
# Windows PowerShell:
./deploy-azure-functions.ps1

# Linux/Mac Bash:
chmod +x deploy-azure-functions.sh
./deploy-azure-functions.sh
```

#### GitHub Actions (Automated)
The repository includes a GitHub Actions workflow that automatically deploys to Azure Functions when you push to the `azure-deployment` branch.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.