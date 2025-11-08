"""Medical Entity schemas"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal

from app.models.medical_entity import EntityType


class MedicalEntityBase(BaseModel):
    """Base medical entity schema"""

    entity_type: EntityType
    entity_data: Dict[str, Any]
    entity_date: Optional[date] = None
    entity_end_date: Optional[date] = None


class MedicalEntityCreate(MedicalEntityBase):
    """Medical entity creation schema"""

    document_id: Optional[UUID] = None
    extraction_confidence: Optional[Decimal] = None


class MedicalEntityUpdate(BaseModel):
    """Medical entity update schema"""

    entity_data: Optional[Dict[str, Any]] = None
    entity_date: Optional[date] = None
    entity_end_date: Optional[date] = None
    is_verified: Optional[bool] = None


class MedicalEntityResponse(MedicalEntityBase):
    """Medical entity response schema"""

    id: UUID
    user_id: UUID
    document_id: Optional[UUID] = None
    extracted_at: datetime
    extraction_confidence: Optional[Decimal] = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
