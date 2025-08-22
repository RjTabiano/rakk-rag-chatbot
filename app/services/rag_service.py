from typing import Tuple, List, Optional
from decimal import Decimal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain_core.documents import Document
from app.services.product_service import search_products_tool
from app.services.pinecone_service import get_vectorstore, embeddings
from app.services.chat_history_service import chat_history_service
from app.core.config import VECTOR_DIMENSION
from app.core.prompts import prompt_template
from app.utils.rag_utils import should_retrieve, build_context


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)


def convert_decimals_to_float(obj):
    """Recursively convert Decimal objects to float in nested data structures."""
    if isinstance(obj, list):
        return [convert_decimals_to_float(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimals_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj


def query_rag(question: str, session_id: Optional[str] = None, namespace: Optional[str] = None, k: int = 5) -> Tuple[str, List[Document], Optional[List[dict]]]:
    # Get conversation history for context
    chat_context = ""
    if session_id:
        chat_context = chat_history_service.get_formatted_history_context(session_id)
    
    # Retrieval phase
    if should_retrieve(question):
        qvec = embeddings.embed_query(question)
        if len(qvec) != VECTOR_DIMENSION:
            raise ValueError(
                f"Query embedding dim {len(qvec)} != index dim {VECTOR_DIMENSION}."
            )
        vs = get_vectorstore(namespace)
        docs = vs.similarity_search_by_vector(qvec, k=k)

        if not docs:
            return "No relevant context found.", [], None

        context = build_context(docs)
    else:
        context, docs = "", []

    # Combine RAG context with chat history
    full_context = f"{chat_context}\n\n{context}" if chat_context else context

    # Agent setup
    agent = initialize_agent(
        tools=[search_products_tool],
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent.agent,
        tools=[search_products_tool],
        return_intermediate_steps=True,
        verbose=True
    )

    # Run agent
    messages = prompt_template.format_messages(context=full_context, question=question)
    result = agent_executor.invoke({"input": messages})

    completion = result["output"]

    products = None
    product_links = None
    if result.get("intermediate_steps"):
        raw_outputs = [step[1] for step in result["intermediate_steps"]]
        products = []
        for output in raw_outputs:
            if isinstance(output, list):
                products.extend(output)
            else:
                products.append(output)
        
        # Convert Decimal objects to float for JSON serialization
        if products:
            products = convert_decimals_to_float(products)
            product_links = [product.get('link') for product in products if product.get('link')]

    # Save conversation to history
    if session_id:
        chat_history_service.save_conversation(
            session_id=session_id,
            user_message=question,
            bot_response=completion,
            product_context=products,
            product_links=product_links
        )

    return completion, docs, products


def clear_chat_session(session_id: str) -> None:
    """Clear chat history for a session when it ends."""
    chat_history_service.clear_session_history(session_id)


def get_chat_history(session_id: str) -> List[dict]:
    """Get chat history for a session."""
    return chat_history_service.get_conversation_history(session_id)
