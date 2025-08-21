"""
Lightweight text chunking utility.
Replaces langchain text splitters with simple implementation.
"""
from typing import List, Dict, Any
import re

def split_docs_simple(docs: List[Dict[str, Any]], chunk_size: int = 1000, chunk_overlap: int = 150) -> List[Dict[str, Any]]:
    """
    Simple document splitting without langchain dependencies.
    
    Args:
        docs: List of document dictionaries with 'content' key
        chunk_size: Maximum size of each chunk
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of chunk dictionaries
    """
    chunks = []
    
    for doc in docs:
        content = doc.get("content", "")
        title = doc.get("title", "Document")
        
        # Split content into chunks
        text_chunks = split_text(content, chunk_size, chunk_overlap)
        
        for i, chunk_text in enumerate(text_chunks):
            chunk = {
                "content": chunk_text,
                "title": title,
                "chunk_index": i,
                "source": doc.get("source", "unknown")
            }
            chunks.append(chunk)
    
    return chunks

def split_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Split text into chunks with overlap.
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Number of characters to overlap
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If this is not the last chunk and we're in the middle of a word,
        # try to break at a sentence or word boundary
        if end < len(text):
            # Look for sentence boundaries first
            sentence_end = text.rfind('.', start, end)
            if sentence_end > start:
                end = sentence_end + 1
            else:
                # Look for word boundaries
                word_end = text.rfind(' ', start, end)
                if word_end > start:
                    end = word_end
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position considering overlap
        start = max(start + 1, end - chunk_overlap)
        
        # Avoid infinite loop
        if start >= len(text):
            break
    
    return chunks
