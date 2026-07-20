from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, doc_id: int) -> Document | None:
        return self.db.query(Document).filter(Document.id == doc_id).first()

    def list_all(self) -> list[Document]:
        return self.db.query(Document).all()

    def create(self, obj_in: DocumentCreate) -> Document:
        db_obj = Document(
            filename=obj_in.filename,
            file_path=obj_in.file_path,
            doc_type=obj_in.doc_type,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
