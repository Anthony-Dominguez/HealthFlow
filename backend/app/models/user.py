"""User model"""
from sqlalchemy import Column, String, Date, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class User(Base):
    """User model - extends Supabase auth.users"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    phone_number = Column(String, nullable=True)

    # JSON fields for flexibility
    profile_data = Column(JSONB, default={}, server_default="{}")
    preferences = Column(JSONB, default={}, server_default="{}")

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    medical_entities = relationship(
        "MedicalEntity", back_populates="user", cascade="all, delete-orphan"
    )
    timeline_events = relationship(
        "TimelineEvent", back_populates="user", cascade="all, delete-orphan"
    )
    voice_logs = relationship("VoiceLog", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship(
        "ChatSession", back_populates="user", cascade="all, delete-orphan"
    )
    embeddings = relationship("Embedding", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
