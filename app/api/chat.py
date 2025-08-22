from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_service import query_rag, clear_chat_session, get_chat_history
from app.utils.formatter import format_docs_for_llm

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer, docs, products = query_rag(
        question=request.question, 
        session_id=request.session_id,
        namespace=request.namespace, 
        k=request.k
    )
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


@router.delete("/chat/session/{session_id}")
def clear_session(session_id: str):
    """
    Clear chat history for a specific session.
    """
    try:
        clear_chat_session(session_id)
        return {"message": f"Chat history cleared for session: {session_id}"}
    except Exception as e:
        return {"error": f"Failed to clear session: {str(e)}"}


@router.get("/chat/history/{session_id}")
def get_session_history(session_id: str):
    """
    Get chat history for a specific session.
    """
    try:
        history = get_chat_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        return {"error": f"Failed to get history: {str(e)}"}

