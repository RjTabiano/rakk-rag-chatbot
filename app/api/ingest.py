from fastapi import APIRouter, HTTPException
from app.models.ingest import IngestRequest
from app.services.ingest_service import ingest_pdf
import os

router = APIRouter()

@router.post("/ingest")
def ingest(request: IngestRequest):
    if not os.path.exists(request.pdf_path):
        raise HTTPException(status_code=400, detail="PDF not found")
    result = ingest_pdf(
        pdf_path=request.pdf_path,
        namespace=request.namespace,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap
    )
    return result
