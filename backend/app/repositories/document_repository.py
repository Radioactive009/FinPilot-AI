from sqlalchemy.orm import Session
from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db: Session):
        super().__init__(Document, db)

    def get_by_user(self, user_id: any) -> list[Document]:
        return self.db.query(Document).filter(Document.user_id == user_id).all()
