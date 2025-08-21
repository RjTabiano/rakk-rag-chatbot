import os
from typing import Optional
from pinecone import Pinecone, ServerlessSpec
from app.core.config import INDEX_NAME, VECTOR_DIMENSION, PINECONE_API_KEY
from langchain_google_genai import GoogleGenerativeAIEmbeddings

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

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def get_index():
    """Get the Pinecone index."""
    return pc.Index(INDEX_NAME)

def get_vectorstore(namespace: Optional[str] = None):
    """
    Get a simple vector store interface for the Pinecone index.
    This is a custom implementation that works with the new Pinecone API.
    """
    index = get_index()
    
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
    
    return PineconeVectorStore(index, embeddings, namespace)
