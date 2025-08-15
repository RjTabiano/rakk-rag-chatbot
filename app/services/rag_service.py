# rag_service.py
from typing import Tuple, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document

from app.services.pinecone_service import get_vectorstore, embeddings
from app.core.config import VECTOR_DIMENSION

# LLM setup
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

SYSTEM_PROMPT = """
You are ShopBot, a friendly and helpful e-commerce support assistant for our online store.
Your job is to answer questions conversationally — like a real customer service representative —
while still being accurate and concise.

Guidelines:
- Use the provided context whenever possible. If no context exists, answer to the best of your knowledge.
- Speak naturally, using "you" and "we" to make the customer feel heard.
- Summarize and explain instead of dumping raw lists, unless the customer asks for a list.
- Mention important details in a clear, easy-to-read way.
- Keep answers short but informative — avoid long walls of text.
- When citing sources, blend them into your reply naturally, like:
  "According to our warranty policy (source: title, chunk_id)..."
- Always aim to sound warm, approachable, and professional — like live chat support.
"""


prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Context:\n{context}\n\nQuestion:\n{question}")
])


def query_rag(question: str, namespace: str | None = None, k: int = 5) -> Tuple[str, List[Document]]:

    #Embed the question
    qvec = embeddings.embed_query(question)
    if len(qvec) != VECTOR_DIMENSION:
        raise ValueError(
            f"Query embedding dim {len(qvec)} != index dim {VECTOR_DIMENSION}. "
            "Ensure the embeddings model matches the Pinecone index."
        )

    #Get LangChain vectorstore & search
    vs = get_vectorstore(namespace)
    docs = vs.similarity_search_by_vector(qvec, k=k)

    if not docs:
        return "No relevant context found.", []

    #Build context string with sources
    context_chunks = []
    for d in docs:
        title = d.metadata.get("title") or d.metadata.get("source") or "unknown"
        chunk_id = d.metadata.get("chunk_id") or "n/a"
        context_chunks.append(f"{d.page_content}\n[source: {title}, {chunk_id}]")
    context = "\n\n---\n\n".join(context_chunks)

    # 4) Ask the LLM
    messages = prompt_template.format_messages(context=context, question=question)
    completion = llm.invoke(messages)
    answer_text = completion.content or "No answer generated."

    return answer_text, docs
