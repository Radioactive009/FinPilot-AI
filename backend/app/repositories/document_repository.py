import uuid
from datetime import datetime, timezone
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

    def queue_document(self, doc_id: uuid.UUID) -> Optional[Document]:
        doc = self.get(doc_id)
        if doc:
            doc.processing_status = "QUEUED"
            self.db.commit()
            self.db.refresh(doc)
        return doc

    def start_processing(self, doc_id: uuid.UUID) -> Optional[Document]:
        doc = self.get(doc_id)
        if doc:
            doc.processing_status = "PROCESSING"
            doc.processing_started_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(doc)
        return doc

    def finish_processing(self, doc_id: uuid.UUID) -> Optional[Document]:
        doc = self.get(doc_id)
        if doc:
            doc.processing_status = "PARSED"
            now = datetime.now(timezone.utc)
            doc.processing_completed_at = now
            doc.processed_at = now
            self.db.commit()
            self.db.refresh(doc)
        return doc

    def fail_processing(self, doc_id: uuid.UUID, error_msg: str) -> Optional[Document]:
        doc = self.get(doc_id)
        if doc:
            doc.processing_status = "FAILED"
            doc.processing_error = error_msg
            doc.processing_completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(doc)
        return doc
