from sqlalchemy.orm import Session
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentResponse
from app.models.document import Document


class DocumentService:
    def __init__(self, db: Session):
        self.repository = DocumentRepository(db)

    def upload_and_process(self, filename: str, file_path: str, doc_type: str) -> Document:
        obj_in = DocumentCreate(filename=filename, file_path=file_path, doc_type=doc_type)
        doc = self.repository.create(obj_in)
        # Placeholder for trigger parser / ocr / embed
        return doc

    def get_all_documents(self) -> list[Document]:
        return self.repository.list_all()
