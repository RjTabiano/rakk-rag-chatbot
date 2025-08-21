"""
Runtime configuration and dependency validation for Python 3.12.
This file ensures compatibility across different deployment environments.
"""

import sys
import warnings
from typing import Tuple

# Minimum required Python version
MIN_PYTHON_VERSION = (3, 12, 0)


def check_python_version() -> bool:
    """
    Check if the current Python version meets the minimum requirements.
    
    Returns:
        bool: True if version is compatible, False otherwise
    """
    current_version = sys.version_info[:3]
    
    if current_version < MIN_PYTHON_VERSION:
        raise RuntimeError(
            f"Python {'.'.join(map(str, MIN_PYTHON_VERSION))} or higher is required. "
            f"Current version: {'.'.join(map(str, current_version))}"
        )
    
    return True


def validate_dependencies() -> bool:
    """
    Validate that all required dependencies are available and compatible.
    
    Returns:
        bool: True if all dependencies are valid
    """
    required_packages = [
        'fastapi',
        'uvicorn',
        'langchain',
        'langchain_google_genai',
        'langchain_pinecone',
        'pinecone',
        'pypdf',
        'python_dotenv',
        'mysql.connector'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        raise ImportError(
            f"Missing required packages: {', '.join(missing_packages)}. "
            f"Please run 'pip install -r requirements.txt'"
        )
    
    return True


def initialize_runtime() -> None:
    """
    Initialize the runtime environment with proper checks.
    """
    check_python_version()
    validate_dependencies()
    
    # Suppress deprecation warnings for cleaner logs in production
    if not sys.flags.dev_mode:
        warnings.filterwarnings("ignore", category=DeprecationWarning)


# Run initialization when module is imported
if __name__ != "__main__":
    initialize_runtime()
