import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict


class InvoiceItemBase(BaseModel):
    description: str
    quantity: float = 1.00
    unit_price: float = 0.00
    amount: float = 0.00


class InvoiceItemCreate(InvoiceItemBase):
    invoice_id: uuid.UUID


class InvoiceItemUpdate(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None


class InvoiceItemResponse(InvoiceItemBase):
    id: uuid.UUID
    invoice_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
