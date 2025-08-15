from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document

def load_pdf(pdf_path: str, title: str = "Ecommerce PDF") -> list[Document]:
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    for d in docs:
        meta = d.metadata or {}
        meta.setdefault("title", title)
        d.metadata = meta
    return docs