"""Document schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from uuid import UUID

from app.models.document import DocumentType, ProcessingStatus


class DocumentBase(BaseModel):
    """Base document schema"""

    file_name: str
    document_type: DocumentType
    document_subtype: Optional[str] = None
    document_date: Optional[date] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class DocumentCreate(DocumentBase):
    """Document creation schema"""

    storage_path: str
    mime_type: str
    file_size: int


class DocumentUpdate(BaseModel):
    """Document update schema"""

    document_type: Optional[DocumentType] = None
    document_subtype: Optional[str] = None
    document_date: Optional[date] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentUpload(BaseModel):
    """Document upload response schema"""

    document_id: UUID
    upload_url: Optional[str] = None
    message: str


class DocumentResponse(DocumentBase):
    """Document response schema"""

    id: UUID
    user_id: UUID
    storage_path: str
    mime_type: str
    file_size: int
    processing_status: ProcessingStatus
    processing_error: Optional[str] = None
    extracted_text: Optional[str] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentList(BaseModel):
    """Document list response"""

    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
