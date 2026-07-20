import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.document import Document
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, db: Session):
        super().__init__(Invoice, db)

    def get_invoice(self, invoice_id: uuid.UUID) -> Optional[Invoice]:
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()

    def list_invoices(self, user_id: uuid.UUID, is_admin: bool = False) -> List[Invoice]:
        if is_admin:
            return self.db.query(Invoice).all()
        return (
            self.db.query(Invoice)
            .join(Document, Invoice.document_id == Document.id)
            .filter(Document.user_id == user_id)
            .all()
        )

    def get_by_number_and_vendor(self, invoice_number: str, vendor_id: uuid.UUID) -> Optional[Invoice]:
        return (
            self.db.query(Invoice)
            .filter(Invoice.invoice_number == invoice_number, Invoice.vendor_id == vendor_id)
            .first()
        )

    def create_invoice(self, invoice_obj: Invoice) -> Invoice:
        self.db.add(invoice_obj)
        self.db.commit()
        self.db.refresh(invoice_obj)
        return invoice_obj
