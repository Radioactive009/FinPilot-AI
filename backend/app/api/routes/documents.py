import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User, UserRole
from app.models.document import DocumentType
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService

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
