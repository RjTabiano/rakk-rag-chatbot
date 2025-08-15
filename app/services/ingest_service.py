from app.utils.pdf_loader import load_pdf
from app.utils.chunking import split_docs
from app.services.pinecone_service import get_vectorstore
from langchain_core.documents import Document

def ingest_pdf(pdf_path: str, namespace: str = None, chunk_size: int = 1000, chunk_overlap: int = 150) -> dict:
    docs: list[Document] = load_pdf(pdf_path)
    chunks = split_docs(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    for i, chunk in enumerate(chunks):
        meta = chunk.metadata or {}
        meta["chunk_id"] = f"chunk-{i}"
        meta["source"] = pdf_path
        chunk.metadata = meta
    vs = get_vectorstore(namespace)
    vs.add_documents(chunks)
    return {"chunks_indexed": len(chunks), "namespace": namespace}
