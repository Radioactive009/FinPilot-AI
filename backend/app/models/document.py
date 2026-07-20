import enum
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.session import Base


class DocumentType(str, enum.Enum):
    INVOICE = "Invoice"
    EXPENSE_REPORT = "Expense Report"
    AUDIT_REPORT = "Audit Report"
    POLICY = "Policy"
    VENDOR_STATEMENT = "Vendor Statement"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., pdf, png
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    upload_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, success, failed
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    uploaded_by: Mapped["User"] = relationship("User", back_populates="documents")
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="document", cascade="all, delete-orphan")

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.invoice import Invoice
