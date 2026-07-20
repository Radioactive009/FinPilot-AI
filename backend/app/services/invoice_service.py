import uuid
from sqlalchemy.orm import Session
from app.repositories.invoice_repository import InvoiceRepository
from app.schemas.invoice import InvoiceCreate
from app.models.invoice import Invoice


class InvoiceService:
    def __init__(self, db: Session):
        self.repository = InvoiceRepository(db)

    def create_invoice(self, schema_in: InvoiceCreate) -> Invoice:
        db_obj = Invoice(
            document_id=schema_in.document_id,
            vendor_id=schema_in.vendor_id,
            invoice_number=schema_in.invoice_number,
            invoice_date=schema_in.invoice_date,
            due_date=schema_in.due_date,
            currency=schema_in.currency,
            subtotal=schema_in.subtotal,
            tax=schema_in.tax,
            total_amount=schema_in.total_amount,
            payment_status=schema_in.payment_status,
            validation_status=schema_in.validation_status,
            confidence_score=schema_in.confidence_score,
        )
        return self.repository.create(db_obj)

    def get_invoice(self, invoice_id: uuid.UUID) -> Invoice | None:
        return self.repository.get(invoice_id)
