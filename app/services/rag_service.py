from typing import Tuple, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain_core.documents import Document
from app.services.product_service import search_products_tool
from app.services.pinecone_service import get_vectorstore, embeddings
from app.core.config import VECTOR_DIMENSION
from app.core.prompts import prompt_template
from app.utils.rag_utils import should_retrieve, build_context


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)


def query_rag(question: str, namespace: Optional[str] = None, k: int = 5) -> Tuple[str, List[Document], Optional[List[dict]]]:
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
    messages = prompt_template.format_messages(context=context, question=question)
    result = agent_executor.invoke({"input": messages})

    completion = result["output"]

    # Extract products (flatten lists if needed)
    products = None
    if result.get("intermediate_steps"):
        raw_outputs = [step[1] for step in result["intermediate_steps"]]
        products = []
        for output in raw_outputs:
            if isinstance(output, list):
                products.extend(output)
            else:
                products.append(output)

    return completion, docs, products
