import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db: Session):
        super().__init__(Document, db)

    def list_documents(self, user_id: uuid.UUID, is_admin: bool = False) -> List[Document]:
        if is_admin:
            return self.db.query(Document).all()
        return self.db.query(Document).filter(Document.user_id == user_id).all()
