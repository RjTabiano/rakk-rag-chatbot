#!/bin/bash

# Azure App Service startup script for Python web apps
echo "Starting RakkA.I(RAG) FastAPI application..."

# Set environment variables for production
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"
export PORT=${PORT:-8000}

# Azure App Service automatically installs dependencies from requirements.txt
# No need to manually install packages in production

# Start the FastAPI application using gunicorn for production
echo "Starting FastAPI application with gunicorn..."
python -m gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120
