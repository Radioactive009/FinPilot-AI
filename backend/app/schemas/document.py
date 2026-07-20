import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.document import DocumentType


class DocumentBase(BaseModel):
    file_name: str
    original_file_name: str
    file_type: str
    document_type: DocumentType
    file_path: str
    upload_status: str = "pending"


class DocumentCreate(DocumentBase):
    user_id: uuid.UUID


class DocumentUpdate(BaseModel):
    file_name: Optional[str] = None
    original_file_name: Optional[str] = None
    file_type: Optional[str] = None
    document_type: Optional[DocumentType] = None
    file_path: Optional[str] = None
    upload_status: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
