"""
Vercel serverless function entry point for the RAG chatbot API.
This file serves as the main entry point for deployment on Vercel.
"""

import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
app_dir = current_dir.parent / "app"
sys.path.insert(0, str(app_dir))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import logging
    
    from api import chat, ingest
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    app = FastAPI(
        title="E-commerce RAG Chatbot", 
        version="1.0.0",
        description="AI-powered chatbot for e-commerce support using RAG (Retrieval Augmented Generation)"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(ingest.router, prefix="/api", tags=["Ingest"])
    app.include_router(chat.router, prefix="/api", tags=["Chat"])

    @app.get("/")
    def root():
        """Root endpoint for the E-commerce RAG Chatbot API."""
        return {
            "message": "Welcome to the E-commerce RAG Chatbot API",
            "version": "1.0.0",
            "status": "active",
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
        """Health check endpoint for monitoring and deployment verification."""
        return {
            "status": "healthy", 
            "service": "rag-chatbot",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "runtime": "vercel-python3.12"
        }

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler for better error reporting."""
        logger.error(f"Global exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc) if hasattr(app, 'debug') and app.debug else "An unexpected error occurred"
            }
        )

except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="RAG Chatbot - Error State")
    
    @app.get("/")
    def error_root():
        return {
            "error": "Application failed to initialize",
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
