from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []

class URLIngestRequest(BaseModel):
    url: str
