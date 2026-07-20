import uuid
from sqlalchemy.orm import Session
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate
from app.models.document import Document, DocumentType


class DocumentService:
    def __init__(self, db: Session):
        self.repository = DocumentRepository(db)

    def upload_document(
        self, user_id: uuid.UUID, file_name: str, original_file_name: str, file_type: str, document_type: DocumentType, file_path: str
    ) -> Document:
        schema_in = DocumentCreate(
            user_id=user_id,
            file_name=file_name,
            original_file_name=original_file_name,
            file_type=file_type,
            document_type=document_type,
            file_path=file_path,
        )
        # Create using base repository create
        db_obj = Document(
            user_id=schema_in.user_id,
            file_name=schema_in.file_name,
            original_file_name=schema_in.original_file_name,
            file_type=schema_in.file_type,
            document_type=schema_in.document_type,
            file_path=schema_in.file_path,
        )
        return self.repository.create(db_obj)

    def get_document(self, doc_id: uuid.UUID) -> Document | None:
        return self.repository.get(doc_id)

    def list_documents(self) -> list[Document]:
        return self.repository.list()
