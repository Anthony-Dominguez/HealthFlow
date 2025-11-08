"""Timeline schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from uuid import UUID

from app.models.timeline import EventType


class TimelineEventBase(BaseModel):
    """Base timeline event schema"""

    event_type: EventType
    title: str
    description: Optional[str] = None
    event_date: date
    event_timestamp: Optional[datetime] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class TimelineEventCreate(TimelineEventBase):
    """Timeline event creation schema"""

    document_id: Optional[UUID] = None
    medical_entity_ids: List[UUID] = []


class TimelineEventUpdate(BaseModel):
    """Timeline event update schema"""

    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[date] = None
    event_timestamp: Optional[datetime] = None
    is_starred: Optional[bool] = None
    user_notes: Optional[str] = None
    tags: Optional[List[str]] = None


class TimelineEventResponse(TimelineEventBase):
    """Timeline event response schema"""

    id: UUID
    user_id: UUID
    document_id: Optional[UUID] = None
    is_starred: bool
    user_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
