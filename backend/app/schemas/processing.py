import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DocumentProcessResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    message: str


class DocumentStatusResponse(BaseModel):
    document_id: uuid.UUID
    processing_status: str
    processing_error: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
