"""
Optimized Vercel entry point for lightweight deployment.
Uses only essential dependencies to stay under 250MB limit.
"""
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
current_dir = Path(__file__).parent
app_dir = current_dir.parent / "app"
sys.path.insert(0, str(app_dir))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import logging
    
    # Import lightweight API modules
    from api import chat_lite, ingest_lite
    
    # Configure minimal logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    app = FastAPI(
        title="E-commerce RAG Chatbot - Optimized", 
        version="2.0.0",
        description="Lightweight RAG chatbot optimized for Vercel deployment (<250MB)"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include optimized routers
    app.include_router(ingest_lite.router, prefix="/api", tags=["Ingest"])
    app.include_router(chat_lite.router, prefix="/api", tags=["Chat"])

    @app.get("/")
    def root():
        """Root endpoint."""
        return {
            "message": "Welcome to the E-commerce RAG Chatbot API - Optimized",
            "version": "2.0.0",
            "status": "active",
            "optimization": "lightweight (<250MB)",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "endpoints": {
                "health": "/health",
                "chat": "/api/chat", 
                "ingest": "/api/ingest",
                "docs": "/docs"
            }
        }

    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy", 
            "service": "rag-chatbot-lite",
            "version": "2.0.0",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "optimization": "lightweight"
        }

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler."""
        logger.error(f"Global exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc),
                "service": "rag-chatbot-lite"
            }
        )

except Exception as e:
    # Fallback if imports fail
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="RAG Chatbot - Error State")
    
    @app.get("/")
    def error_root():
        return {
            "error": "Optimized application failed to initialize",
            "message": str(e),
            "status": "error"
        }
    
    @app.get("/health")
    def error_health():
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
