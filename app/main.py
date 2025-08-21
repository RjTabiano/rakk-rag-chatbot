from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, ingest  

app = FastAPI(title="E-commerce RAG Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(ingest.router, tags=["Ingest"])
app.include_router(chat.router, tags=["Chat"])

@app.get("/")
def root():
    return {"message": "Welcome to the E-commerce RAG Chatbot API"}

@app.get("/health")
def health_check():
    """Health check endpoint for Azure App Service."""
    return {"status": "healthy", "service": "E-commerce RAG Chatbot API"}
