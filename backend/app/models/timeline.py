"""Timeline models"""
from sqlalchemy import Column, String, Date, Text, TIMESTAMP, Enum, ForeignKey, Boolean, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class EventType(str, enum.Enum):
    """Event type enum"""

    LAB_COMPLETED = "lab_completed"
    MEDICATION_STARTED = "medication_started"
    MEDICATION_ENDED = "medication_ended"
    SYMPTOM_LOGGED = "symptom_logged"
    APPOINTMENT_SCHEDULED = "appointment_scheduled"
    APPOINTMENT_COMPLETED = "appointment_completed"
    PROCEDURE_COMPLETED = "procedure_completed"
    DIAGNOSIS_RECEIVED = "diagnosis_received"
    DOCUMENT_UPLOADED = "document_uploaded"
    VITAL_RECORDED = "vital_recorded"
    IMMUNIZATION_RECEIVED = "immunization_received"


# Association table for many-to-many relationship
class TimelineEventEntity(Base):
    """Join table for timeline events and medical entities"""

    __tablename__ = "timeline_event_entities"

    timeline_event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("timeline_events.id", ondelete="CASCADE"),
        primary_key=True,
    )
    medical_entity_id = Column(
        UUID(as_uuid=True),
        ForeignKey("medical_entities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class TimelineEvent(Base):
    """Timeline event model"""

    __tablename__ = "timeline_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )

    # Event classification
    event_type = Column(Enum(EventType), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Temporal information
    event_date = Column(Date, nullable=False, index=True)
    event_timestamp = Column(TIMESTAMP(timezone=True), nullable=True)

    # Additional data
    doc_metadata = Column(JSONB, default={}, server_default="{}")
    tags = Column(ARRAY(String), default=[], server_default="{}")

    # User interaction
    is_starred = Column(Boolean, default=False, server_default="false")
    user_notes = Column(Text, nullable=True)

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user = relationship("User", back_populates="timeline_events")
    document = relationship("Document", back_populates="timeline_events")
    medical_entities = relationship(
        "MedicalEntity",
        secondary="timeline_event_entities",
        back_populates="timeline_events",
    )

    def __repr__(self):
        return f"<TimelineEvent {self.title} - {self.event_date}>"
