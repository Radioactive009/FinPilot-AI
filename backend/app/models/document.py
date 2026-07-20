import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, func
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
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType), nullable=False
    )
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # in bytes
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    upload_status: Mapped[str] = mapped_column(String(50), default="Uploaded", nullable=False)  # Uploaded, Failed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Processing state tracking (Sprint 4)
    processing_status: Mapped[str] = mapped_column(String(50), default="UPLOADED", nullable=False)  # UPLOADED, QUEUED, PROCESSING, PARSED, FAILED
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_error: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    uploaded_by: Mapped["User"] = relationship("User", back_populates="documents")
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="document", cascade="all, delete-orphan")

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.invoice import Invoice
