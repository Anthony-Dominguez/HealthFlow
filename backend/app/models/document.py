"""Document model"""
from sqlalchemy import Column, String, BigInteger, Date, Text, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class DocumentType(str, enum.Enum):
    """Document type enum"""

    LAB_REPORT = "lab_report"
    MEDICATION_LIST = "medication_list"
    DISCHARGE_SUMMARY = "discharge_summary"
    IMAGING_REPORT = "imaging_report"
    PRESCRIPTION = "prescription"
    INSURANCE_CARD = "insurance_card"
    INSURANCE_EOB = "insurance_eob"
    VACCINATION_RECORD = "vaccination_record"
    ALLERGY_LIST = "allergy_list"
    CARE_PLAN = "care_plan"
    VISIT_SUMMARY = "visit_summary"
    REFERRAL = "referral"
    VOICE_NOTE = "voice_note"
    OTHER = "other"


class ProcessingStatus(str, enum.Enum):
    """Processing status enum"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


class Document(Base):
    """Document model"""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # File information
    file_name = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)

    # Document classification
    document_type = Column(Enum(DocumentType), nullable=False)
    document_subtype = Column(String, nullable=True)

    # Processing
    processing_status = Column(Enum(ProcessingStatus), nullable=False, default=ProcessingStatus.PENDING)
    processing_error = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)

    # Metadata
    doc_metadata = Column(JSONB, default={}, server_default="{}")
    tags = Column(ARRAY(String), default=[], server_default="{}")

    # Dates
    document_date = Column(Date, nullable=True)
    uploaded_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    processed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user = relationship("User", back_populates="documents")
    medical_entities = relationship("MedicalEntity", back_populates="document")
    timeline_events = relationship("TimelineEvent", back_populates="document")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document {self.file_name}>"
