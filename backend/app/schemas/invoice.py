import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.invoice_item import InvoiceItemResponse


class InvoiceBase(BaseModel):
    invoice_number: str
    invoice_date: date
    due_date: Optional[date] = None
    currency: str = "USD"
    subtotal: float = 0.00
    tax: float = 0.00
    total_amount: float = 0.00
    payment_status: str = "unpaid"
    validation_status: str = "pending"
    confidence_score: float = Field(default=0.0000, ge=0.0, le=1.0)


class InvoiceCreate(InvoiceBase):
    document_id: uuid.UUID
    vendor_id: uuid.UUID


class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    currency: Optional[str] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None
    payment_status: Optional[str] = None
    validation_status: Optional[str] = None
    confidence_score: Optional[float] = None


class InvoiceResponse(InvoiceBase):
    id: uuid.UUID
    document_id: uuid.UUID
    vendor_id: uuid.UUID
    created_at: datetime
    items: List[InvoiceItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
