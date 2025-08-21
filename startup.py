#!/usr/bin/env python3
"""
Azure App Service startup script for RakkA.I(RAG) application.
This script configures and starts the FastAPI application on Azure.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main startup function for Azure App Service."""
    logger.info("Starting RakkA.I(RAG) application on Azure App Service")
    
    # Add app directory to Python path
    app_dir = Path(__file__).parent / "app"
    sys.path.insert(0, str(app_dir))
    
    # Set Azure App Service specific paths
    if os.path.exists("/home/site/wwwroot"):
        sys.path.insert(0, "/home/site/wwwroot")
    
    # Set default port for Azure App Service
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Python path: {sys.path}")
    
    # Import and run the FastAPI application
    try:
        import uvicorn
        from app.main import app
        
        # Configure for production
        config = {
            "host": host,
            "port": port,
            "log_level": "info",
            "access_log": True,
            "workers": 1,  # Azure App Service manages scaling
            "timeout_keep_alive": 120
        }
        
        logger.info(f"Starting with config: {config}")
        
        # Run the application
        uvicorn.run("app.main:app", **config)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
