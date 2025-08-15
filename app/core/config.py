import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "ecom-rag")
RAG_NAMESPACE = os.getenv("RAG_NAMESPACE", "prod-v1")
VECTOR_DIMENSION = 768
