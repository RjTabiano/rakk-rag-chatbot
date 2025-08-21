import azure.functions as func
import logging
import sys
from pathlib import Path

# Add app directory to Python path
current_dir = Path(__file__).parent
app_dir = current_dir / "app"
sys.path.insert(0, str(app_dir))

# Import the FastAPI app
from app.main import app as fastapi_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Azure Function App with FastAPI integration
app = func.AsgiFunctionApp(
    app=fastapi_app, 
    http_auth_level=func.AuthLevel.ANONYMOUS
)

logger.info("Azure Functions FastAPI app initialized successfully")
