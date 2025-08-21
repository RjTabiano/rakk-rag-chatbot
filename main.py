from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pathlib import Path

# Add app directory to path for imports
current_dir = Path(__file__).parent
app_dir = current_dir / "app"
sys.path.insert(0, str(app_dir))

# Create FastAPI app
app = FastAPI(title="E-commerce RAG Chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Basic endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to the E-commerce RAG Chatbot API"}

@app.get("/health")
def health_check():
    """Health check endpoint for Azure Functions."""
    return {"status": "healthy", "service": "E-commerce RAG Chatbot API"}

@app.get("/test")
def test_imports():
    """Test if we can import our modules."""
    try:
        # Try importing our modules
        from api import chat, ingest
        return {
            "status": "success", 
            "message": "All imports successful",
            "modules": ["chat", "ingest"]
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Import failed: {str(e)}",
            "python_path": sys.path[:3]
        }

# Try to include routers if available
try:
    from api import chat, ingest
    app.include_router(ingest.router, tags=["Ingest"])
    app.include_router(chat.router, tags=["Chat"])
    print("✅ Successfully included FastAPI routers")
except Exception as e:
    print(f"⚠️ Could not include routers: {e}")
    # Add basic endpoints as fallback
    
    @app.get("/chat")
    def chat_placeholder():
        return {"message": "Chat endpoint placeholder - full implementation loading..."}
    
    @app.get("/ingest")
    def ingest_placeholder():
        return {"message": "Ingest endpoint placeholder - full implementation loading..."}
