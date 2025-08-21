from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from typing import List

def load_pdf(pdf_path: str, title: str = "Ecommerce PDF") -> List[Document]:
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    for d in docs:
        meta = d.metadata or {}
        meta.setdefault("title", title)
        d.metadata = meta
    return docs