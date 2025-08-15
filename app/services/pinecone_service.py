import os
from pinecone import Pinecone, ServerlessSpec
from app.core.config import INDEX_NAME, VECTOR_DIMENSION, PINECONE_API_KEY
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore

# Create Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

CLOUD = "aws"
REGION = "us-east-1"

# Create index if it doesn't exist
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=VECTOR_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud=CLOUD, region=REGION)
    )

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


# LangChain vector store wrapper
def get_vectorstore(namespace: str = None) -> PineconeVectorStore:
    return PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings, namespace=namespace)
