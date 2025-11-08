"""Chat models"""
from sqlalchemy import Column, String, Text, TIMESTAMP, Enum, ForeignKey, Integer, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class MessageRole(str, enum.Enum):
    """Message role enum"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatSession(Base):
    """Chat session model"""

    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Session info
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)

    # Metadata
    doc_metadata = Column(JSONB, default={}, server_default="{}")

    # Temporal
    started_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    last_message_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession {self.id} - {self.title}>"


class ChatMessage(Base):
    """Chat message model"""

    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Message content
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # Metadata
    doc_metadata = Column(JSONB, default={}, server_default="{}")
    token_count = Column(Integer, nullable=True)

    # Model information (for assistant messages)
    model_name = Column(String, nullable=True)
    model_version = Column(String, nullable=True)

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    references = relationship(
        "ChatMessageReference", back_populates="message", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ChatMessage {self.role} - {self.id}>"


class ChatMessageReference(Base):
    """Chat message reference model - links messages to documents and entities"""

    __tablename__ = "chat_message_references"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_message_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Reference targets (one must be non-null)
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True
    )
    medical_entity_id = Column(
        UUID(as_uuid=True), ForeignKey("medical_entities.id", ondelete="CASCADE"), nullable=True
    )

    # Context
    reference_type = Column(String, nullable=True)
    relevance_score = Column(Numeric(3, 2), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "(document_id IS NOT NULL) OR (medical_entity_id IS NOT NULL)",
            name="check_reference_target",
        ),
    )

    # Relationships
    message = relationship("ChatMessage", back_populates="references")

    def __repr__(self):
        return f"<ChatMessageReference {self.id}>"
