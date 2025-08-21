"""
Lightweight PDF loader that doesn't depend on LangChain.
"""
from typing import List, Dict, Any
import pypdf
import io

def load_pdf_simple(pdf_path: str, title: str = "Ecommerce PDF") -> List[Dict[str, Any]]:
    """
    Load PDF using pypdf without LangChain dependencies.
    
    Args:
        pdf_path: Path to the PDF file
        title: Title for the document
        
    Returns:
        List of document dictionaries
    """
    documents = []
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                
                if text.strip():  # Only add pages with content
                    doc = {
                        "content": text,
                        "title": title,
                        "source": pdf_path,
                        "page": page_num + 1
                    }
                    documents.append(doc)
                    
    except Exception as e:
        raise Exception(f"Error loading PDF {pdf_path}: {str(e)}")
    
    return documents

# Keep original function for backward compatibility but make it lightweight
def load_pdf(pdf_path: str, title: str = "Ecommerce PDF") -> List[Dict[str, Any]]:
    """Backward compatible PDF loader."""
    return load_pdf_simple(pdf_path, title)
