from typing import List
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: Session):
        super().__init__(Payment, db)

    def get_by_invoice(self, invoice_id: any) -> List[Payment]:
        return self.db.query(Payment).filter(Payment.invoice_id == invoice_id).all()
