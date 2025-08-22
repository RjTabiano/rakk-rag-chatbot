from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ProductItem(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    image: Optional[str] = None
    link: Optional[str] = None

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    namespace: Optional[str] = None
    k: int = 5

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    products: Optional[List[ProductItem]] = None
