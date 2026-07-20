from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Placeholder for file processing / DB record / OCR
    return {
        "filename": file.filename,
        "status": "uploaded",
        "processed": False
    }


@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Placeholder for listing database records
    return []
