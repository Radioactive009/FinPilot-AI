import uuid
from datetime import datetime, date
from typing import List
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.session import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False
    )
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    tax: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    payment_status: Mapped[str] = mapped_column(String(50), default="unpaid", nullable=False)  # unpaid, paid, partial
    validation_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, verified, error
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 4), default=0.0000, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="invoices")
    document: Mapped["Document"] = relationship("Document", back_populates="invoices")
    items: Mapped[List["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.vendor import Vendor
    from app.models.document import Document
    from app.models.invoice_item import InvoiceItem
    from app.models.payment import Payment
