import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User, UserRole
from app.models.document import DocumentType
from app.schemas.document import DocumentResponse
from app.schemas.processing import DocumentProcessResponse, DocumentStatusResponse
from app.services.document_service import DocumentService
from app.services.processing_service import DocumentProcessingService

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    document_service = DocumentService(db)
    return document_service.upload_document(
        user_id=current_user.id, file=file, document_type=document_type
    )


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    document_service = DocumentService(db)
    is_admin = current_user.role == UserRole.ADMIN
    return document_service.list_documents(user_id=current_user.id, is_admin=is_admin)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    document_service = DocumentService(db)
    is_admin = current_user.role == UserRole.ADMIN
    return document_service.get_document(
        doc_id=document_id, user_id=current_user.id, is_admin=is_admin
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    document_service = DocumentService(db)
    is_admin = current_user.role == UserRole.ADMIN
    document_service.delete_document(
        doc_id=document_id, user_id=current_user.id, is_admin=is_admin
    )
    return None


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
def process_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    processing_service = DocumentProcessingService(db)
    is_admin = current_user.role == UserRole.ADMIN
    
    # 1. Queue document (auth checks inside service)
    processing_service.queue_document(doc_id=document_id, user_id=current_user.id, is_admin=is_admin)
    
    # 2. Simulate processing execution immediately
    processing_service.process_document(doc_id=document_id)
    
    return {
        "document_id": document_id,
        "status": "Queued & Processed",
        "message": "Document queued and simulated metadata extraction completed."
    }


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    document_service = DocumentService(db)
    is_admin = current_user.role == UserRole.ADMIN
    doc = document_service.get_document(doc_id=document_id, user_id=current_user.id, is_admin=is_admin)
    
    return {
        "document_id": doc.id,
        "processing_status": doc.processing_status,
        "processing_error": doc.processing_error,
        "processing_started_at": doc.processing_started_at,
        "processing_completed_at": doc.processing_completed_at,
        "processed_at": doc.processed_at,
    }
