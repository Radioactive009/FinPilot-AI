import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.document import DocumentType


class DocumentBase(BaseModel):
    original_filename: str
    stored_filename: str
    document_type: DocumentType
    mime_type: str
    file_size: int
    storage_path: str
    upload_status: str = "Uploaded"


class DocumentCreate(DocumentBase):
    user_id: uuid.UUID


class DocumentUpdate(BaseModel):
    original_filename: Optional[str] = None
    stored_filename: Optional[str] = None
    document_type: Optional[DocumentType] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    storage_path: Optional[str] = None
    upload_status: Optional[str] = None
    processing_status: Optional[str] = None
    processing_error: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    
    # Processing pipeline fields
    processing_status: str
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    processed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
