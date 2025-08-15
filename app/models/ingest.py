from pydantic import BaseModel
from typing import Optional

class IngestRequest(BaseModel):
    pdf_path: str
    namespace: Optional[str] = None
    chunk_size: int = 1000
    chunk_overlap: int = 150
