"""
Lightweight embeddings service for Google Generative AI.
Removes heavy langchain-google-genai dependency for smaller deployment.
"""
import requests
import json
from typing import List, Optional
from app.core.config import GOOGLE_API_KEY

class LightweightGoogleEmbeddings:
    """Lightweight Google embeddings client that doesn't depend on langchain."""
    
    def __init__(self, model: str = "models/embedding-001"):
        self.model = model
        self.api_key = GOOGLE_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single text query."""
        return self.embed_documents([text])[0]
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        embeddings = []
        
        for text in texts:
            url = f"{self.base_url}/{self.model}:embedContent"
            params = {"key": self.api_key}
            
            data = {
                "model": self.model,
                "content": {
                    "parts": [{"text": text}]
                }
            }
            
            response = requests.post(
                url,
                params=params,
                headers={"Content-Type": "application/json"},
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                embedding = result["embedding"]["values"]
                embeddings.append(embedding)
            else:
                raise Exception(f"Embedding API error: {response.status_code} - {response.text}")
        
        return embeddings

# Global instance
embeddings = LightweightGoogleEmbeddings()
