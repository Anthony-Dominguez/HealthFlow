"""Medical Entity endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.medical_entity import MedicalEntity, EntityType
from app.schemas.medical_entity import (
    MedicalEntityCreate,
    MedicalEntityUpdate,
    MedicalEntityResponse,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=MedicalEntityResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_entity(
    entity_data: MedicalEntityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new medical entity"""
    entity = MedicalEntity(user_id=current_user.id, **entity_data.model_dump())
    db.add(entity)
    await db.commit()
    await db.refresh(entity)
    return entity


@router.get("/", response_model=PaginatedResponse)
async def list_medical_entities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    entity_type: EntityType = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all medical entities for the current user"""
    query = select(MedicalEntity).where(MedicalEntity.user_id == current_user.id)

    if entity_type:
        query = query.where(MedicalEntity.entity_type == entity_type)

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((page - 1) * page_size).limit(page_size).order_by(
        MedicalEntity.entity_date.desc()
    )
    result = await db.execute(query)
    entities = result.scalars().all()

    return PaginatedResponse.create(
        items=[MedicalEntityResponse.model_validate(e) for e in entities],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{entity_id}", response_model=MedicalEntityResponse)
async def get_medical_entity(
    entity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific medical entity"""
    result = await db.execute(
        select(MedicalEntity).where(
            MedicalEntity.id == entity_id, MedicalEntity.user_id == current_user.id
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medical entity not found"
        )

    return entity


@router.put("/{entity_id}", response_model=MedicalEntityResponse)
async def update_medical_entity(
    entity_id: UUID,
    entity_update: MedicalEntityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a medical entity"""
    result = await db.execute(
        select(MedicalEntity).where(
            MedicalEntity.id == entity_id, MedicalEntity.user_id == current_user.id
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medical entity not found"
        )

    for field, value in entity_update.model_dump(exclude_unset=True).items():
        setattr(entity, field, value)

    await db.commit()
    await db.refresh(entity)
    return entity


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_entity(
    entity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a medical entity"""
    result = await db.execute(
        select(MedicalEntity).where(
            MedicalEntity.id == entity_id, MedicalEntity.user_id == current_user.id
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medical entity not found"
        )

    await db.delete(entity)
    await db.commit()
