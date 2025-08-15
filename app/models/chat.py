from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    question: str
    namespace: Optional[str] = None
    k: int = 5

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
