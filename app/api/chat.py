from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_service import query_rag, clear_chat_session, get_chat_history
from app.utils.formatter import format_docs_for_llm
from app.utils.db_connection import get_db_connection
from app.core.config import DB_DATABASE

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


@router.get("/db-status")
def check_database_connection():
    """
    Check database connection status and display database name.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test connection with a simple query
        cursor.execute("SELECT DATABASE() as db_name, CONNECTION_ID() as connection_id, NOW() as current_time")
        result = cursor.fetchone()
        
        # Get additional database info
        cursor.execute("SELECT VERSION() as mysql_version")
        version_result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "connected",
            "database_name": DB_DATABASE,
            "active_database": result[0],
            "connection_id": result[1],
            "current_time": result[2].isoformat() if result[2] else None,
            "mysql_version": version_result[0] if version_result else None,
            "message": f"Successfully connected to database: {DB_DATABASE}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "database_name": DB_DATABASE,
            "error": str(e),
            "message": f"Failed to connect to database: {DB_DATABASE}"
        }


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

