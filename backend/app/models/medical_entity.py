"""Medical Entity model"""
from sqlalchemy import Column, Date, TIMESTAMP, Enum, ForeignKey, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class EntityType(str, enum.Enum):
    """Entity type enum"""

    MEDICATION = "medication"
    LAB_RESULT = "lab_result"
    DIAGNOSIS = "diagnosis"
    SYMPTOM = "symptom"
    DOCTOR = "doctor"
    APPOINTMENT = "appointment"
    PROCEDURE = "procedure"
    ALLERGY = "allergy"
    VITAL_SIGN = "vital_sign"
    IMMUNIZATION = "immunization"


class MedicalEntity(Base):
    """Medical entity model - structured medical data extracted from documents"""

    __tablename__ = "medical_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )

    # Entity classification
    entity_type = Column(Enum(EntityType), nullable=False, index=True)

    # Flexible entity data (varies by type)
    entity_data = Column(JSONB, nullable=False)

    # Temporal information
    entity_date = Column(Date, nullable=True, index=True)
    entity_end_date = Column(Date, nullable=True)

    # Extraction metadata
    extracted_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    extraction_confidence = Column(Numeric(3, 2), nullable=True)
    is_verified = Column(Boolean, default=False, server_default="false")

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user = relationship("User", back_populates="medical_entities")
    document = relationship("Document", back_populates="medical_entities")
    timeline_events = relationship(
        "TimelineEvent",
        secondary="timeline_event_entities",
        back_populates="medical_entities",
    )

    def __repr__(self):
        return f"<MedicalEntity {self.entity_type} - {self.id}>"
