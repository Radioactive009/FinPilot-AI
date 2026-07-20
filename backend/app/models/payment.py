import uuid
from datetime import date
from sqlalchemy import String, Numeric, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.session import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False
    )
    payment_reference: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)  # Bank Transfer, Credit Card, Cash, etc.
    payment_status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)  # pending, completed, failed

    # Relationships
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.invoice import Invoice
