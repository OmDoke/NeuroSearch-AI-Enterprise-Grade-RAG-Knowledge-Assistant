from fastapi import APIRouter
from backend.schemas import ChatRequest, ChatResponse
from backend.services.rag_pipeline import get_answer

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    answer, sources = get_answer(request.query, request.session_id)
    return ChatResponse(answer=answer, sources=sources)
