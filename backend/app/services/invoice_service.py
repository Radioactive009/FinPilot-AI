import uuid
from datetime import datetime, date
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentType
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.vendor import Vendor
from app.parsers.parser_factory import ParserFactory
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.document_repository import DocumentRepository
from app.core.logging import logger


class InvoiceExtractionService:
    def __init__(self, db: Session):
        self.db = db
        self.invoice_repository = InvoiceRepository(db)
        self.document_repository = DocumentRepository(db)

    def extract_invoice(
        self, document_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool = False
    ) -> Invoice:
        logger.info("Initializing invoice extraction", document_id=str(document_id))

        # 1. Fetch document and verify authorization
        doc = self.document_repository.get(document_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        if doc.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this document",
            )

        # 2. Supported Documents Check
        if doc.document_type != DocumentType.INVOICE:
            logger.warning(
                "Attempted extraction on non-invoice document type",
                document_id=str(document_id),
                type=doc.document_type
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extraction is only supported for Invoice documents. Current type: {doc.document_type}",
            )

        # 3. Resolve Parser & Execute Parsing
        parser = ParserFactory.get_parser(doc.document_type)
        try:
            parsed_data = parser.parse(doc.storage_path)
            logger.info("Document parsed successfully", document_id=str(document_id))
        except Exception as e:
            error_msg = f"Parser execution failed: {str(e)}"
            logger.error(error_msg, document_id=str(document_id))
            self.document_repository.fail_processing(document_id, error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg,
            )

        # 4. Validation Layer
        required_fields = ["invoice_number", "vendor_name", "invoice_date", "total_amount"]
        missing_fields = [field for field in required_fields if not parsed_data.get(field)]

        if missing_fields:
            error_msg = f"Validation failed: missing required fields: {', '.join(missing_fields)}"
            logger.error(error_msg, document_id=str(document_id))
            # Mark document processing as FAILED and record error message
            self.document_repository.fail_processing(document_id, error_msg)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )

        # 5. Resolve/Create Vendor
        vendor_name = parsed_data["vendor_name"]
        vendor = self.db.query(Vendor).filter(Vendor.vendor_name == vendor_name).first()
        if not vendor:
            # Generate unique vendor code
            clean_name = "".join(c for c in vendor_name if c.isalnum()).upper()
            vendor_code = f"VND_{clean_name}_{uuid.uuid4().hex[:6]}"
            vendor = Vendor(
                vendor_name=vendor_name,
                vendor_code=vendor_code
            )
            self.db.add(vendor)
            self.db.commit()
            self.db.refresh(vendor)
            logger.info("Created new vendor", vendor_id=str(vendor.id), name=vendor_name)

        # 6. Duplicate Prevention Check
        invoice_number = parsed_data["invoice_number"]
        existing_invoice = self.invoice_repository.get_by_number_and_vendor(
            invoice_number=invoice_number, vendor_id=vendor.id
        )
        if existing_invoice:
            error_msg = "Invoice number already exists for this vendor"
            logger.warning(
                error_msg,
                invoice_number=invoice_number,
                vendor_id=str(vendor.id)
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )

        # Parse string dates to date objects
        def parse_date(date_str: Optional[str]) -> Optional[date]:
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return None

        # 7. Create Invoice
        invoice_date_obj = parse_date(parsed_data["invoice_date"]) or date.today()
        due_date_obj = parse_date(parsed_data.get("due_date"))

        invoice_obj = Invoice(
            document_id=document_id,
            vendor_id=vendor.id,
            invoice_number=invoice_number,
            invoice_date=invoice_date_obj,
            due_date=due_date_obj,
            currency=parsed_data.get("currency", "USD"),
            subtotal=parsed_data.get("subtotal", 0.0),
            tax=parsed_data.get("tax", 0.0),
            total_amount=parsed_data["total_amount"],
            validation_status="verified",
            confidence_score=1.0000
        )
        
        # Populate Invoice Items
        items_data = parsed_data.get("items", [])
        for item in items_data:
            invoice_item = InvoiceItem(
                description=item["description"],
                quantity=item.get("quantity", 1.0),
                unit_price=item.get("unit_price", 0.0),
                amount=item.get("amount", 0.0)
            )
            invoice_obj.items.append(invoice_item)

        # Save to DB and finish document processing state
        invoice = self.invoice_repository.create_invoice(invoice_obj)
        self.document_repository.finish_processing(document_id)
        
        logger.info(
            "Invoice extracted and saved successfully",
            invoice_id=str(invoice.id),
            document_id=str(document_id)
        )
        return invoice

    def get_invoice(
        self, invoice_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool = False
    ) -> Invoice:
        invoice = self.invoice_repository.get_invoice(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )

        # Access check via linked Document
        doc = self.document_repository.get(invoice.document_id)
        if not doc or (doc.user_id != user_id and not is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this invoice",
            )

        return invoice

    def list_invoices(self, user_id: uuid.UUID, is_admin: bool = False) -> List[Invoice]:
        return self.invoice_repository.list_invoices(user_id, is_admin)
