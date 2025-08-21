"""
Optimized main application using lightweight components.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import lightweight API routes
from app.api import chat_lite, ingest_lite

app = FastAPI(
    title="E-commerce RAG Chatbot - Optimized", 
    version="2.0.0",
    description="Lightweight RAG chatbot optimized for Vercel deployment"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Include optimized routers
app.include_router(ingest_lite.router, tags=["Ingest"])
app.include_router(chat_lite.router, tags=["Chat"])

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the E-commerce RAG Chatbot API - Optimized",
        "version": "2.0.0",
        "status": "active",
        "optimization": "lightweight"
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "rag-chatbot-lite",
        "version": "2.0.0"
    }
