from typing import List
from langchain_core.documents import Document

def should_retrieve(question: str) -> bool:
    keywords = ["price", "order", "shipping", "delivery", "return", "warranty", "product"]
    return any(word in question.lower() for word in keywords)


def build_context(docs: List[Document]) -> str:
    if not docs:
        return ""

    context_chunks = []
    for d in docs:
        title = d.metadata.get("title") or d.metadata.get("source") or "unknown"
        chunk_id = d.metadata.get("chunk_id") or "n/a"
        context_chunks.append(f"{d.page_content}\n[source: {title}, {chunk_id}]")

    return "\n\n---\n\n".join(context_chunks)
