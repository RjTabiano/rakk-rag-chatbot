"""
Optimized Pinecone service for lightweight Vercel deployment.
Removes langchain-pinecone dependency and uses direct Pinecone client.
"""
import os
from typing import Optional, List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from app.core.config import INDEX_NAME, VECTOR_DIMENSION, PINECONE_API_KEY

# Initialize Pinecone with the new API
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if it doesn't exist
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=VECTOR_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

def get_index():
    """Get the Pinecone index."""
    return pc.Index(INDEX_NAME)

class LightweightVectorStore:
    """Lightweight vector store that doesn't depend on langchain-pinecone."""
    
    def __init__(self, namespace: Optional[str] = None):
        self.index = get_index()
        self.namespace = namespace
        
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
        """Add documents with their embeddings to the vector store."""
        vectors = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            # Create unique vector ID
            chunk_id = doc.get("chunk_id", str(i))
            vector_id = f"{self.namespace}_{chunk_id}" if self.namespace else chunk_id
            
            # Prepare metadata
            metadata = doc.copy()
            
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })
        
        # Upsert vectors to Pinecone
        self.index.upsert(vectors=vectors, namespace=self.namespace)
        return len(vectors)
        
    def similarity_search_by_vector(self, embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents by embedding vector."""
        results = self.index.query(
            vector=embedding,
            top_k=k,
            include_metadata=True,
            namespace=self.namespace
        )
        
        # Convert results to simple dictionaries
        documents = []
        for match in results.matches:
            doc = {
                "content": match.metadata.get("text", ""),
                "metadata": match.metadata,
                "score": match.score
            }
            documents.append(doc)
        
        return documents

def get_vectorstore(namespace: Optional[str] = None) -> LightweightVectorStore:
    """Get a lightweight vector store instance."""
    return LightweightVectorStore(namespace)
