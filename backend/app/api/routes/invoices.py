import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.dependencies import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.invoice import InvoiceResponse
from app.services.invoice_service import InvoiceExtractionService

router = APIRouter()


@router.post("/{document_id}/extract", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def extract_invoice(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = InvoiceExtractionService(db)
    is_admin = current_user.role == UserRole.ADMIN
    return service.extract_invoice(
        document_id=document_id, user_id=current_user.id, is_admin=is_admin
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = InvoiceExtractionService(db)
    is_admin = current_user.role == UserRole.ADMIN
    return service.get_invoice(
        invoice_id=invoice_id, user_id=current_user.id, is_admin=is_admin
    )


@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = InvoiceExtractionService(db)
    is_admin = current_user.role == UserRole.ADMIN
    return service.list_invoices(user_id=current_user.id, is_admin=is_admin)
