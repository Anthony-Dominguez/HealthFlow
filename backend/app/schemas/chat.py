"""Chat schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from app.models.chat import MessageRole


class ChatSessionBase(BaseModel):
    """Base chat session schema"""

    title: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    """Chat session creation schema"""

    pass


class ChatSessionResponse(ChatSessionBase):
    """Chat session response schema"""

    id: UUID
    user_id: UUID
    summary: Optional[str] = None
    started_at: datetime
    last_message_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageBase(BaseModel):
    """Base chat message schema"""

    role: MessageRole
    content: str


class ChatMessageCreate(ChatMessageBase):
    """Chat message creation schema"""

    session_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = {}


class ChatMessageResponse(ChatMessageBase):
    """Chat message response schema"""

    id: UUID
    session_id: UUID
    user_id: UUID
    metadata: Dict[str, Any]
    token_count: Optional[int] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    """Chat request schema"""

    message: str
    session_id: Optional[UUID] = None
    include_history: bool = True
    max_history: int = 10


class ChatResponse(BaseModel):
    """Chat response schema"""

    session_id: UUID
    message: ChatMessageResponse
    sources: Optional[List[Dict[str, Any]]] = []
