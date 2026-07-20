import uuid
from sqlalchemy.orm import Session
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment import PaymentCreate
from app.models.payment import Payment


class PaymentService:
    def __init__(self, db: Session):
        self.repository = PaymentRepository(db)

    def record_payment(self, schema_in: PaymentCreate) -> Payment:
        db_obj = Payment(
            invoice_id=schema_in.invoice_id,
            payment_reference=schema_in.payment_reference,
            payment_date=schema_in.payment_date,
            payment_amount=schema_in.payment_amount,
            payment_method=schema_in.payment_method,
            payment_status=schema_in.payment_status,
        )
        return self.repository.create(db_obj)

    def get_payments_for_invoice(self, invoice_id: uuid.UUID) -> list[Payment]:
        return self.repository.get_by_invoice(invoice_id)
