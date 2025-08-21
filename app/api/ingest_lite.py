"""
Optimized ingest API using lightweight components.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
import os

# Import lightweight services
from app.services.ingest_service_lite import ingest_pdf

router = APIRouter()

# Request model
class IngestRequest(BaseModel):
    pdf_path: str
    namespace: Optional[str] = None
    chunk_size: int = 1000
    chunk_overlap: int = 150

@router.post("/ingest")
def ingest(request: IngestRequest):
    """
    Ingest endpoint using optimized ingest service.
    """
    try:
        if not os.path.exists(request.pdf_path):
            raise HTTPException(status_code=400, detail="PDF file not found")
        
        result = ingest_pdf(
            pdf_path=request.pdf_path,
            namespace=request.namespace,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Ingestion failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
