import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class DocumentText(BaseModel):
    document_id: Optional[uuid.UUID] = None
    page_number: int
    raw_text: str
    confidence: float
    metadata: Dict[str, Any] = {}


class DocumentTextResponse(BaseModel):
    document_id: uuid.UUID
    pages: List[DocumentText]
    total_pages: int
    extractor_used: str
