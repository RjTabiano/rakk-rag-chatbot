import azure.functions as func
import logging
import sys
import os
from pathlib import Path

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_python_path():
    """Setup Python path for Azure Functions."""
    current_dir = Path(__file__).parent.absolute()
    app_dir = current_dir / "app"
    
    # Add directories to Python path
    paths_to_add = [str(current_dir), str(app_dir)]
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # Set PYTHONPATH environment variable
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    new_pythonpath = ':'.join(paths_to_add + [current_pythonpath] if current_pythonpath else paths_to_add)
    os.environ['PYTHONPATH'] = new_pythonpath
    
    logger.info(f"Python path configured: {sys.path[:3]}...")  # Log first 3 entries
    return current_dir, app_dir

def import_fastapi_app():
    """Import the FastAPI application with error handling."""
    try:
        # Try importing the FastAPI app
        from app.main import app as fastapi_app
        logger.info("✅ Successfully imported FastAPI app from app.main")
        return fastapi_app
    except ImportError as e:
        logger.error(f"❌ Failed to import FastAPI app: {e}")
        # Try alternative import path
        try:
            import main
            fastapi_app = main.app
            logger.info("✅ Successfully imported FastAPI app from main")
            return fastapi_app
        except Exception as e2:
            logger.error(f"❌ Alternative import also failed: {e2}")
            raise e

# Setup environment
current_dir, app_dir = setup_python_path()

# Import FastAPI app
try:
    fastapi_app = import_fastapi_app()
    
    # Create Azure Function App with FastAPI integration
    app = func.AsgiFunctionApp(
        app=fastapi_app, 
        http_auth_level=func.AuthLevel.ANONYMOUS
    )
    
    logger.info("🚀 Azure Functions FastAPI app initialized successfully")
    
except Exception as e:
    logger.error(f"💥 Failed to initialize Azure Functions app: {e}")
    import traceback
    logger.error(f"Stack trace: {traceback.format_exc()}")
    
    # Create a minimal function app as fallback
    app = func.FunctionApp()
    
    @app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
    def health_check(req: func.HttpRequest) -> func.HttpResponse:
        return func.HttpResponse("Function app is running but FastAPI failed to initialize", status_code=500)
    
    logger.info("📋 Created fallback function app with health check")
