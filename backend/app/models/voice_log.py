"""Voice Log model"""
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class VoiceLog(Base):
    """Voice log model - voice-recorded symptom journals and notes"""

    __tablename__ = "voice_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )

    # Audio file
    audio_storage_path = Column(String, nullable=False)
    audio_format = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Transcription
    transcribed_text = Column(Text, nullable=True)
    transcription_confidence = Column(Numeric(3, 2), nullable=True)
    transcription_language = Column(String, default="en", server_default="en")

    # Metadata
    doc_metadata = Column(JSONB, default={}, server_default="{}")
    tags = Column(ARRAY(String), default=[], server_default="{}")

    # Temporal
    recorded_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user = relationship("User", back_populates="voice_logs")

    def __repr__(self):
        return f"<VoiceLog {self.id} - {self.recorded_at}>"
