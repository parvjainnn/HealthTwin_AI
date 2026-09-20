from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import os
import shutil
from pathlib import Path
from app.services.chatbot import ingest_document

router = APIRouter(prefix="/api", tags=["upload"])

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document to be indexed for the medical chatbot's knowledge base."""
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    file_path = DATA_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Trigger document ingestion
        ingested = await ingest_document(str(file_path))
        
        if not ingested:
            raise HTTPException(status_code=500, detail="Failed to ingest document into the vector store.")
            
        return {"filename": file.filename, "message": "File uploaded and successfully added to the knowledge base.", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
