from fastapi import FastAPI
from app.api import chat, ingest  

app = FastAPI(title="E-commerce RAG Chatbot")

# Include routers
app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/")
def root():
    return {"message": "Welcome to the E-commerce RAG Chatbot API"}
