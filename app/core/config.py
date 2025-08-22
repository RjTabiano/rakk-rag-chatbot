import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and External Service Configuration
GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")

# Pinecone Configuration
INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "ecom-rag")
RAG_NAMESPACE: str = os.getenv("RAG_NAMESPACE", "prod-v1")
VECTOR_DIMENSION: int = 768

# Database Configuration
DB_HOST: Optional[str] = os.getenv("DB_HOST")
DB_PORT: Optional[str] = os.getenv("DB_PORT")
DB_DATABASE: Optional[str] = os.getenv("DB_DATABASE")
DB_USERNAME: Optional[str] = os.getenv("DB_USERNAME")
DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")

# Application Configuration
APP_URL: Optional[str] = os.getenv("APP_URL")

# Validation function for required environment variables
def validate_config() -> None:
    """Validate that all required configuration variables are set."""
    required_vars = {
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "PINECONE_API_KEY": PINECONE_API_KEY,
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_DATABASE": DB_DATABASE,
        "DB_USERNAME": DB_USERNAME,
        "DB_PASSWORD": DB_PASSWORD,
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}. "
            "Please check your .env file or environment configuration."
        )

