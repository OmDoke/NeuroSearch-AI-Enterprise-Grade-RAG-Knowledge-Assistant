from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.services.embeddings import get_vector_store
from backend.schemas import URLIngestRequest
import tempfile
import os

router = APIRouter()

@router.post("/file")
async def ingest_file(file: UploadFile = File(...)):
    vs = get_vector_store()
    if not vs:
        raise HTTPException(status_code=500, detail="Vector store not initialized. Missing Pinecone API keys.")
        
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name

        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        vs.add_documents(splits)
        
        os.remove(temp_path)
        return {"status": "success", "message": f"Successfully ingested {len(splits)} chunks from {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/url")
async def ingest_url(request: URLIngestRequest):
    vs = get_vector_store()
    if not vs:
        raise HTTPException(status_code=500, detail="Vector store not initialized. Missing Pinecone API keys.")
        
    try:
        loader = WebBaseLoader(request.url)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        vs.add_documents(splits)
        return {"status": "success", "message": f"Successfully ingested {len(splits)} chunks from URL"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
