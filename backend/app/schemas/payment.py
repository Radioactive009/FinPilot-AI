import uuid
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PaymentBase(BaseModel):
    payment_reference: str
    payment_date: date
    payment_amount: float = 0.00
    payment_method: str
    payment_status: str = "completed"


class PaymentCreate(PaymentBase):
    invoice_id: uuid.UUID


class PaymentUpdate(BaseModel):
    payment_reference: Optional[str] = None
    payment_date: Optional[date] = None
    payment_amount: Optional[float] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None


class PaymentResponse(PaymentBase):
    id: uuid.UUID
    invoice_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
