import os
import uuid
from pathlib import Path
from typing import List
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.document_repository import DocumentRepository
from app.models.document import Document, DocumentType

# Allowed validation criteria
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "csv", "xlsx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

# Document Type folder mapping
SUBFOLDER_MAPPING = {
    DocumentType.INVOICE: "invoices",
    DocumentType.EXPENSE_REPORT: "expense_reports",
    DocumentType.AUDIT_REPORT: "audit_reports",
    DocumentType.POLICY: "policies",
    DocumentType.VENDOR_STATEMENT: "vendor_statements",
}


class DocumentService:
    def __init__(self, db: Session):
        self.repository = DocumentRepository(db)

    def upload_document(
        self, user_id: uuid.UUID, file: UploadFile, document_type: DocumentType
    ) -> Document:
        # 1. Validation: Reject empty files
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)  # Reset pointer

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        # 2. Validation: Maximum file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 20 MB limit",
            )

        # 3. Validation: Extensions & MIME types
        filename_str = file.filename or ""
        ext = filename_str.split(".")[-1].lower() if "." in filename_str else ""
        if ext not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format or extension. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # 4. Storage folder resolution
        subfolder = SUBFOLDER_MAPPING.get(document_type)
        if not subfolder:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid document type",
            )

        target_dir = settings.UPLOADS_DIR / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)

        # 5. Unique UUID filename retention
        unique_id = uuid.uuid4()
        stored_filename = f"{unique_id}.{ext}"
        storage_path = str(target_dir / stored_filename)

        # Save to disk
        try:
            with open(storage_path, "wb") as buffer:
                buffer.write(file.file.read())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save file to disk",
            )

        # 6. Database record creation
        db_obj = Document(
            user_id=user_id,
            original_filename=filename_str,
            stored_filename=stored_filename,
            document_type=document_type,
            mime_type=file.content_type,
            file_size=file_size,
            storage_path=storage_path,
            upload_status="Uploaded",
        )
        return self.repository.create(db_obj)

    def delete_document(
        self, doc_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool = False
    ) -> Document:
        doc = self.repository.get(doc_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Authorization: owner or admin only
        if doc.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to delete this document",
            )

        # Remove from disk if exists
        if os.path.exists(doc.storage_path):
            try:
                os.remove(doc.storage_path)
            except Exception:
                pass  # Fail gracefully on file removal but proceed with database cleanup

        return self.repository.delete(doc_id)

    def get_document(
        self, doc_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool = False
    ) -> Document:
        doc = self.repository.get(doc_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Authorization: owner or admin only
        if doc.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to view this document",
            )

        return doc

    def list_documents(self, user_id: uuid.UUID, is_admin: bool = False) -> List[Document]:
        return self.repository.list_documents(user_id, is_admin)
