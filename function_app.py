import azure.functions as func
import logging
import sys
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup Python path
current_dir = Path(__file__).parent.absolute()
app_dir = current_dir / "app"

# Add directories to Python path
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(app_dir))

logger.info(f"Function app starting...")
logger.info(f"Current directory: {current_dir}")
logger.info(f"App directory: {app_dir}")

# Create the function app
app = func.FunctionApp()

@app.function_name(name="health")
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    logger.info('Health check endpoint hit.')
    
    response_data = {
        "status": "healthy",
        "service": "E-commerce RAG Chatbot API",
        "message": "Azure Functions is running"
    }
    
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=200,
        headers={"Content-Type": "application/json"}
    )

@app.function_name(name="root")
@app.route(route="", auth_level=func.AuthLevel.ANONYMOUS)
def root_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """Root endpoint."""
    logger.info('Root endpoint hit.')
    
    response_data = {
        "message": "Welcome to the E-commerce RAG Chatbot API",
        "endpoints": {
            "health": "/health",
            "docs": "/docs (not available in this simplified version)",
            "chat": "/chat (to be implemented)",
            "ingest": "/ingest (to be implemented)"
        }
    }
    
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=200,
        headers={"Content-Type": "application/json"}
    )

@app.function_name(name="test_import")
@app.route(route="test", auth_level=func.AuthLevel.ANONYMOUS)
def test_import(req: func.HttpRequest) -> func.HttpResponse:
    """Test if we can import the FastAPI app."""
    logger.info('Test import endpoint hit.')
    
    try:
        from app.main import app as fastapi_app
        from app.api import chat, ingest
        
        response_data = {
            "status": "success",
            "message": "FastAPI app imported successfully",
            "fastapi_title": getattr(fastapi_app, 'title', 'Unknown'),
            "routes_available": True
        }
        status_code = 200
        
    except Exception as e:
        logger.error(f"Import test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        response_data = {
            "status": "error",
            "message": f"Failed to import FastAPI app: {str(e)}",
            "python_path": sys.path[:3],
            "current_dir": str(current_dir),
            "app_dir": str(app_dir)
        }
        status_code = 500
    
    return func.HttpResponse(
        json.dumps(response_data),
        status_code=status_code,
        headers={"Content-Type": "application/json"}
    )

logger.info("Azure Functions app initialized successfully")
