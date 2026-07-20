from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, db: Session):
        super().__init__(Invoice, db)

    def get_by_invoice_number(self, invoice_number: str) -> Optional[Invoice]:
        return self.db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()

    def get_by_vendor(self, vendor_id: any) -> List[Invoice]:
        return self.db.query(Invoice).filter(Invoice.vendor_id == vendor_id).all()
