"""
Optimized chat API using lightweight components.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Import lightweight services
from app.services.rag_service_lite import query_rag

router = APIRouter()

# Request/Response models
class ChatRequest(BaseModel):
    question: str
    namespace: Optional[str] = None
    k: int = 5

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    products: Optional[List[Dict[str, Any]]] = None

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat endpoint using optimized RAG service.
    """
    try:
        answer, docs, products = query_rag(
            question=request.question, 
            namespace=request.namespace, 
            k=request.k
        )
        
        # Format sources
        sources = []
        for doc in docs:
            metadata = doc.get("metadata", {})
            sources.append({
                "title": metadata.get("title", "Unknown"),
                "chunk_id": metadata.get("chunk_id", "N/A"),
                "source": metadata.get("source", "Unknown"),
                "score": doc.get("score", 0.0)
            })
        
        return ChatResponse(
            answer=answer, 
            sources=sources, 
            products=products
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health():
    """Health check endpoint for API testing."""
    return {"status": "ok", "service": "chat-api-lite"}
