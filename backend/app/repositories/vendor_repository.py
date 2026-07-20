from typing import Optional
from sqlalchemy.orm import Session
from app.models.vendor import Vendor
from app.repositories.base import BaseRepository


class VendorRepository(BaseRepository[Vendor]):
    def __init__(self, db: Session):
        super().__init__(Vendor, db)

    def get_by_code(self, vendor_code: str) -> Optional[Vendor]:
        return self.db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()
