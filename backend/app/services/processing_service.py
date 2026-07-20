import os
import uuid
import mimetypes
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.models.document import Document
from app.core.logging import logger


class DocumentProcessingService:
    def __init__(self, db: Session):
        self.repository = DocumentRepository(db)

    def queue_document(
        self, doc_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool = False
    ) -> Document:
        doc = self.repository.get(doc_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Authorization check
        if doc.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to process this document",
            )

        logger.info("Queuing document for processing", doc_id=str(doc_id), user_id=str(user_id))
        return self.repository.queue_document(doc_id)

    def process_document(self, doc_id: uuid.UUID) -> Document:
        logger.info("Starting processing pipeline", doc_id=str(doc_id))
        
        # Start state transition
        doc = self.repository.start_processing(doc_id)
        if not doc:
            logger.error("Failed to start processing, document not found", doc_id=str(doc_id))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        path = doc.storage_path

        # Validate file existence
        if not os.path.exists(path):
            error_msg = "Physical document file not found on disk"
            logger.error("Processing failed", doc_id=str(doc_id), error=error_msg)
            self.repository.fail_processing(doc_id, error_msg)
            return self.repository.get(doc_id)

        try:
            # Simulate parsing by extracting file metadata
            stat_info = os.stat(path)
            
            filename = os.path.basename(path)
            extension = filename.split(".")[-1].lower() if "." in filename else ""
            mime_type = doc.mime_type
            file_size = stat_info.st_size
            
            # Times formatted in ISO format
            creation_time = datetime.fromtimestamp(stat_info.st_ctime, timezone.utc).isoformat()
            modified_time = datetime.fromtimestamp(stat_info.st_mtime, timezone.utc).isoformat()

            metadata = {
                "filename": filename,
                "extension": extension,
                "mime_type": mime_type,
                "file_size": file_size,
                "creation_time": creation_time,
                "last_modified_time": modified_time,
            }

            logger.info(
                "Document metadata extracted successfully",
                doc_id=str(doc_id),
                metadata=metadata
            )

            # Complete state transition
            return self.repository.finish_processing(doc_id)

        except Exception as e:
            error_msg = f"Unexpected error during metadata extraction: {str(e)}"
            logger.error("Processing failed due to exception", doc_id=str(doc_id), error=error_msg)
            self.repository.fail_processing(doc_id, error_msg)
            return self.repository.get(doc_id)
