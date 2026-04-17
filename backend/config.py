import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "neurosearch")

settings = Settings()
