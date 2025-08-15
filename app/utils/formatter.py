from langchain_core.documents import Document
from typing import List

def format_docs_for_llm(docs: List[Document]) -> str:
    lines = []
    for d in docs:
        title = d.metadata.get("title", "Document")
        chunk_id = d.metadata.get("chunk_id", "N/A")
        lines.append(f"[{title}, chunk:{chunk_id}]\n{d.page_content}")
    return "\n\n---\n\n".join(lines)
