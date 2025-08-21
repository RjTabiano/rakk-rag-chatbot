"""
Optimized ingest service using lightweight components.
"""
from typing import List, Optional, Dict, Any
from app.utils.pdf_loader_lite import load_pdf
from app.utils.chunking_lite import split_docs_simple
from app.services.pinecone_service_lite import get_vectorstore
from app.services.embeddings_lite import embeddings

def ingest_pdf(pdf_path: str, namespace: Optional[str] = None, chunk_size: int = 1000, chunk_overlap: int = 150) -> Dict[str, Any]:
    """
    Ingest PDF documents into the vector store using lightweight components.
    
    Args:
        pdf_path: Path to the PDF file
        namespace: Optional namespace for the vector store
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        
    Returns:
        Dictionary with ingestion results
    """
    try:
        # Load PDF
        docs = load_pdf(pdf_path)
        
        # Split documents into chunks
        chunks = split_docs_simple(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        # Prepare documents and generate embeddings
        documents = []
        texts = []
        
        for i, chunk in enumerate(chunks):
            doc_dict = {
                "text": chunk["content"],
                "chunk_id": f"chunk-{i}",
                "source": pdf_path,
                "title": chunk.get("title", "PDF Document")
            }
            documents.append(doc_dict)
            texts.append(chunk["content"])
        
        # Generate embeddings
        embeddings_list = embeddings.embed_documents(texts)
        
        # Store in vector database
        vs = get_vectorstore(namespace)
        num_indexed = vs.add_documents(documents, embeddings_list)
        
        return {
            "chunks_indexed": num_indexed,
            "namespace": namespace,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed",
            "chunks_indexed": 0
        }
