"""Timeline endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.timeline import TimelineEvent, EventType
from app.schemas.timeline import (
    TimelineEventCreate,
    TimelineEventUpdate,
    TimelineEventResponse,
)
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=TimelineEventResponse, status_code=status.HTTP_201_CREATED)
async def create_timeline_event(
    event_data: TimelineEventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new timeline event"""
    event = TimelineEvent(user_id=current_user.id, **event_data.model_dump(exclude={"medical_entity_ids"}))
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/", response_model=PaginatedResponse)
async def list_timeline_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    event_type: EventType = None,
    start_date: date = None,
    end_date: date = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all timeline events for the current user"""
    query = select(TimelineEvent).where(TimelineEvent.user_id == current_user.id)

    if event_type:
        query = query.where(TimelineEvent.event_type == event_type)
    if start_date:
        query = query.where(TimelineEvent.event_date >= start_date)
    if end_date:
        query = query.where(TimelineEvent.event_date <= end_date)

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    query = query.offset((page - 1) * page_size).limit(page_size).order_by(
        TimelineEvent.event_date.desc()
    )
    result = await db.execute(query)
    events = result.scalars().all()

    return PaginatedResponse.create(
        items=[TimelineEventResponse.model_validate(e) for e in events],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{event_id}", response_model=TimelineEventResponse)
async def get_timeline_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific timeline event"""
    result = await db.execute(
        select(TimelineEvent).where(
            TimelineEvent.id == event_id, TimelineEvent.user_id == current_user.id
        )
    )
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Timeline event not found"
        )

    return event


@router.put("/{event_id}", response_model=TimelineEventResponse)
async def update_timeline_event(
    event_id: UUID,
    event_update: TimelineEventUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a timeline event"""
    result = await db.execute(
        select(TimelineEvent).where(
            TimelineEvent.id == event_id, TimelineEvent.user_id == current_user.id
        )
    )
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Timeline event not found"
        )

    for field, value in event_update.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timeline_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a timeline event"""
    result = await db.execute(
        select(TimelineEvent).where(
            TimelineEvent.id == event_id, TimelineEvent.user_id == current_user.id
        )
    )
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Timeline event not found"
        )

    await db.delete(event)
    await db.commit()
