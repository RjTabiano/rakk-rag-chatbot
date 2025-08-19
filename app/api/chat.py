from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_service import query_rag
from app.utils.formatter import format_docs_for_llm

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer, docs, products = query_rag(request.question, namespace=request.namespace, k=request.k)
    sources = [
        {
            "title": d.metadata.get("title"),
            "chunk_id": d.metadata.get("chunk_id"),
            "source": d.metadata.get("source")
        }
        for d in docs
    ]
    return ChatResponse(
        answer=answer, 
        sources=sources, 
        products=products if products else None
    )


@router.get("/health")
def health():
    """
    Health check endpoint for API testing.
    """
    return {"status": "ok"}

