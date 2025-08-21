import os
import pinecone
from typing import Optional
from app.core.config import INDEX_NAME, VECTOR_DIMENSION, PINECONE_API_KEY, PINECONE_ENVIRONMENT
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Global variables for lazy initialization
_pinecone_initialized = False
_embeddings = None

def init_pinecone():
    """Initialize Pinecone connection lazily."""
    global _pinecone_initialized, _embeddings
    
    if _pinecone_initialized:
        return
    
    try:
        # Initialize Pinecone with the v2 API
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        
        # Create index if it doesn't exist
        if INDEX_NAME not in pinecone.list_indexes():
            pinecone.create_index(
                name=INDEX_NAME,
                dimension=VECTOR_DIMENSION,
                metric="cosine"
            )
        
        _embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        _pinecone_initialized = True
        logger.info("Pinecone initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone: {str(e)}")
        # Don't raise exception to prevent app startup failure
        pass

# Lazy initialization - don't initialize during import

def get_index():
    """Get the Pinecone index."""
    init_pinecone()
    if not _pinecone_initialized:
        raise RuntimeError("Pinecone not properly initialized")
    return pinecone.Index(INDEX_NAME)

def get_embeddings():
    """Get the embeddings instance."""
    init_pinecone()
    if not _embeddings:
        raise RuntimeError("Embeddings not properly initialized")
    return _embeddings

# For backward compatibility
embeddings = property(get_embeddings)

def get_vectorstore(namespace: Optional[str] = None):
    """
    Get a simple vector store interface for the Pinecone index.
    This is a custom implementation that works with the new Pinecone API.
    """
    index = get_index()
    embeddings_instance = get_embeddings()
    
    class PineconeVectorStore:
        def __init__(self, index, embeddings, namespace=None):
            self.index = index
            self.embeddings = embeddings
            self.namespace = namespace
            
        def add_documents(self, documents):
            """Add documents to the vector store."""
            vectors = []
            for i, doc in enumerate(documents):
                # Generate embedding for the document
                embedding = self.embeddings.embed_query(doc.page_content)
                
                # Create unique vector ID
                chunk_id = doc.metadata.get("chunk_id", str(i))
                vector_id = f"{self.namespace}_{chunk_id}" if self.namespace else chunk_id
                
                # Prepare metadata
                metadata = doc.metadata.copy() if doc.metadata else {}
                metadata["text"] = doc.page_content
                
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                })
            
            # Upsert vectors to Pinecone
            self.index.upsert(vectors=vectors, namespace=self.namespace)
            return len(vectors)
            
        def similarity_search_by_vector(self, embedding, k=5):
            """Search for similar documents by embedding vector."""
            results = self.index.query(
                vector=embedding,
                top_k=k,
                include_metadata=True,
                namespace=self.namespace
            )
            
            # Convert results back to Document objects
            from langchain_core.documents import Document
            documents = []
            for match in results.matches:
                metadata = match.metadata.copy()
                text = metadata.pop("text", "")
                documents.append(Document(page_content=text, metadata=metadata))
            
            return documents
    
    return PineconeVectorStore(index, embeddings_instance, namespace)
