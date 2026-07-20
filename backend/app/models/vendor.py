import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.session import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    gst_number: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    address: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="vendor")

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.invoice import Invoice
