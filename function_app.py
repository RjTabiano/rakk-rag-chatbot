import azure.functions as func
import logging
from main import app as fastapi_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Azure Function App with FastAPI integration
app = func.AsgiFunctionApp(
    app=fastapi_app, 
    http_auth_level=func.AuthLevel.ANONYMOUS
)

logger.info("Azure Functions FastAPI app initialized successfully")
