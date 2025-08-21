"""
Optimized RAG service using lightweight components.
Removes heavy langchain dependencies while maintaining full functionality.
"""
from typing import Tuple, List, Optional, Dict, Any
from app.services.llm_lite import llm
from app.services.embeddings_lite import embeddings
from app.services.pinecone_service_lite import get_vectorstore
from app.services.product_service_lite import search_products
from app.core.config import VECTOR_DIMENSION

def should_retrieve(question: str) -> bool:
    """Check if question requires retrieval from vector store."""
    keywords = ["price", "order", "shipping", "delivery", "return", "warranty", "product"]
    return any(word in question.lower() for word in keywords)

def build_context(docs: List[Dict[str, Any]]) -> str:
    """Build context string from retrieved documents."""
    if not docs:
        return ""

    context_chunks = []
    for doc in docs:
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        title = metadata.get("title", "unknown")
        chunk_id = metadata.get("chunk_id", "n/a")
        context_chunks.append(f"{content}\n[source: {title}, {chunk_id}]")

    return "\n\n---\n\n".join(context_chunks)

def query_rag(question: str, namespace: Optional[str] = None, k: int = 5) -> Tuple[str, List[Dict[str, Any]], Optional[List[Dict[str, Any]]]]:
    """
    Main RAG query function with lightweight implementation.
    
    Returns:
        Tuple of (answer, retrieved_docs, products)
    """
    # Retrieval phase
    retrieved_docs = []
    if should_retrieve(question):
        try:
            # Generate query embedding
            query_embedding = embeddings.embed_query(question)
            
            if len(query_embedding) != VECTOR_DIMENSION:
                raise ValueError(
                    f"Query embedding dim {len(query_embedding)} != index dim {VECTOR_DIMENSION}."
                )
            
            # Search vector store
            vs = get_vectorstore(namespace)
            retrieved_docs = vs.similarity_search_by_vector(query_embedding, k=k)
            
            if not retrieved_docs:
                context = "No relevant context found."
            else:
                context = build_context(retrieved_docs)
        except Exception as e:
            print(f"Retrieval error: {e}")
            context = "Error retrieving context."
    else:
        context = ""

    # Product search (if relevant)
    products = None
    if any(word in question.lower() for word in ["product", "buy", "purchase", "price", "cost"]):
        try:
            products = search_products(limit=5)  # Get top 5 products
        except Exception as e:
            print(f"Product search error: {e}")
            products = []

    # Generate response using system prompt
    system_prompt = """
    You are ShopBot, the friendly support assistant for our online store. 
    When chatting with customers, sound warm, approachable, and professional — like a real person in live chat.

    How you should respond:
    - Keep answers short and clear: no more than 2–3 sentences by default.
    - Summarize key details instead of listing everything (e.g., mention warranty length, not all exclusions).
    - If the customer wants more detail, politely offer to expand.
    - Speak naturally, using "you" and "we" to make the customer feel heard.
    - Build rapport if a product is mentioned 
    (e.g., "That's a great choice! Many customers love it.").
    - End with a light follow-up, something like: 
    "Is there anything else I can help you with?" to keep the chat going.
    - Stay positive, supportive, and solution-oriented, even if you can't find an exact answer.

    When recommending products:
    - Only recommend products from the available product list if provided.
    - Do not make up product details; only use information provided.
    - Mention the product name, a brief description, and price.
    - If multiple products match, suggest up to 3 options and highlight their differences.
    - If no products are found, politely inform the customer and offer to help with something else.
    - Never invent product names, prices, or features.

    Your goal: make the shopping experience feel smooth and pleasant,
    like chatting with a friendly store representative who genuinely wants to help.
    """
    
    # Build the prompt
    user_prompt = f"""Context:\n{context}\n\nQuestion:\n{question}"""
    
    try:
        # Generate response
        answer = llm.generate(user_prompt, system_prompt)
    except Exception as e:
        print(f"LLM generation error: {e}")
        answer = "I apologize, but I'm having trouble processing your request right now. Please try again."

    return answer, retrieved_docs, products
