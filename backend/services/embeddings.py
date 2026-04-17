from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Gemini Embeddings
embeddings = None
if settings.GEMINI_API_KEY:
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.GEMINI_API_KEY
        )
    except Exception as e:
        logger.error(f"Error initializing Gemini embeddings: {e}")

# Initialize Pinecone
vector_store = None
if settings.PINECONE_API_KEY and embeddings:
    try:
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index_name = settings.PINECONE_INDEX_NAME
        
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if index_name not in existing_indexes:
            print(f"Creating Pinecone index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=3072, # Gemini enterprise embeddings use 3072 dims
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            # wait for index
            import time
            while not pc.describe_index(index_name).status['ready']:
                time.sleep(1)
        
        vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    except Exception as e:
        logger.error(f"Error initializing Pinecone: {e}")

def get_vector_store():
    return vector_store
