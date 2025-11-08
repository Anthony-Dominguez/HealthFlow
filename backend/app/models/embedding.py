"""Embedding models for RAG"""
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid

from app.core.database import Base


class DocumentChunk(Base):
    """Document chunk model for embedding generation"""

    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Chunk content
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)

    # Chunking metadata
    token_count = Column(Integer, nullable=True)
    char_count = Column(Integer, nullable=True)

    # Context
    doc_metadata = Column(JSONB, default={}, server_default="{}")

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk"),)

    # Relationships
    document = relationship("Document", back_populates="chunks")
    embeddings = relationship("Embedding", back_populates="chunk", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DocumentChunk {self.document_id} - {self.chunk_index}>"


class Embedding(Base):
    """Embedding model for vector search"""

    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(
        UUID(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Vector embedding (dimension 1536 for OpenAI ada-002, adjust as needed)
    embedding_vector = Column(Vector(1536), nullable=False)

    # Model information
    embedding_model = Column(String, nullable=False)
    model_version = Column(String, nullable=True)

    # Audit
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (UniqueConstraint("chunk_id", "embedding_model", name="uq_chunk_model"),)

    # Relationships
    chunk = relationship("DocumentChunk", back_populates="embeddings")
    user = relationship("User", back_populates="embeddings")

    def __repr__(self):
        return f"<Embedding {self.chunk_id} - {self.embedding_model}>"
