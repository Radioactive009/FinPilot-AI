import uuid
from sqlalchemy.orm import Session
from app.repositories.vendor_repository import VendorRepository
from app.schemas.vendor import VendorCreate
from app.models.vendor import Vendor


class VendorService:
    def __init__(self, db: Session):
        self.repository = VendorRepository(db)

    def create_vendor(self, schema_in: VendorCreate) -> Vendor:
        db_obj = Vendor(
            vendor_name=schema_in.vendor_name,
            vendor_code=schema_in.vendor_code,
            gst_number=schema_in.gst_number,
            email=schema_in.email,
            phone=schema_in.phone,
            address=schema_in.address,
        )
        return self.repository.create(db_obj)

    def get_vendor(self, vendor_id: uuid.UUID) -> Vendor | None:
        return self.repository.get(vendor_id)
