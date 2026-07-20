import os
import json
import time
import uuid
from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.document_repository import DocumentRepository
from app.ocr.extractor_factory import ExtractorFactory
from app.schemas.ocr import DocumentTextResponse, DocumentText
from app.core.logging import logger


class OCRExtractionService:
    def __init__(self, db: Session):
        self.document_repository = DocumentRepository(db)

    def extract_text(
        self, document_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool = False
    ) -> DocumentTextResponse:
        logger.info("Initializing text extraction process", document_id=str(document_id))

        doc = self.document_repository.get(document_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Authorization check
        if doc.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this document",
            )

        path = doc.storage_path
        if not os.path.exists(path):
            error_msg = f"Document file not found on disk: {path}"
            logger.error(error_msg, document_id=str(document_id))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found on disk",
            )

        start_time = time.time()
        
        # 1. Resolve Extractor
        extractor = ExtractorFactory.get_extractor(path)
        extractor_name = extractor.__class__.__name__
        
        try:
            # 2. Extract Text
            pages = extractor.extract_text(path)
            processing_time = time.time() - start_time
            
            # Map document_id to each extracted page record
            for page in pages:
                page.document_id = document_id

            # Calculate average confidence
            confidences = [p.confidence for p in pages if p.confidence is not None]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 1.0

            response_obj = DocumentTextResponse(
                document_id=document_id,
                pages=pages,
                total_pages=len(pages),
                extractor_used=extractor_name
            )

            # 3. Save JSON under storage/parsed/
            parsed_dir = settings.STORAGE_DIR / "parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            
            parsed_file_path = parsed_dir / f"{document_id}.json"
            with open(parsed_file_path, "w", encoding="utf-8") as f:
                json.dump(response_obj.model_dump(mode="json"), f, indent=2)

            # Update document status to PARSED
            self.document_repository.finish_processing(document_id)

            logger.info(
                "Document text extraction complete",
                document_id=str(document_id),
                extractor=extractor_name,
                pages=len(pages),
                confidence=avg_confidence,
                processing_time_sec=round(processing_time, 4)
            )

            return response_obj

        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Text extraction failed: {str(e)}"
            logger.error(
                error_msg,
                document_id=str(document_id),
                extractor=extractor_name,
                processing_time_sec=round(processing_time, 4)
            )
            self.document_repository.fail_processing(document_id, error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg,
            )

    def get_parsed_text(
        self, document_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool = False
    ) -> Dict[str, Any]:
        doc = self.document_repository.get(document_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Authorization check
        if doc.user_id != user_id and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this document",
            )

        parsed_file_path = settings.STORAGE_DIR / f"parsed/{document_id}.json"
        if not os.path.exists(parsed_file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parsed text not found. Run text extraction first.",
            )

        try:
            with open(parsed_file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not load parsed text: {str(e)}",
            )
