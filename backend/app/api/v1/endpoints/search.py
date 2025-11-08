"""Search endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.medical_entity import MedicalEntity
from app.schemas.document import DocumentResponse
from app.schemas.medical_entity import MedicalEntityResponse

router = APIRouter()


@router.get("/documents", response_model=List[DocumentResponse])
async def search_documents(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search documents by text

    Uses full-text search on file names and extracted text
    """
    # Simple search - can be enhanced with PostgreSQL full-text search
    search_query = select(Document).where(
        Document.user_id == current_user.id,
        or_(
            Document.file_name.ilike(f"%{query}%"),
            Document.extracted_text.ilike(f"%{query}%"),
        ),
    )

    result = await db.execute(search_query.limit(limit))
    documents = result.scalars().all()
    return documents


@router.get("/entities", response_model=List[MedicalEntityResponse])
async def search_medical_entities(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search medical entities

    Searches within entity_data JSONB field
    """
    # Simple JSONB search
    search_query = select(MedicalEntity).where(
        MedicalEntity.user_id == current_user.id,
        func.cast(MedicalEntity.entity_data, str).ilike(f"%{query}%"),
    )

    result = await db.execute(search_query.limit(limit))
    entities = result.scalars().all()
    return entities


@router.get("/semantic")
async def semantic_search(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    threshold: float = Query(0.7, ge=0.0, le=1.0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Semantic search using embeddings

    This endpoint:
    1. Generates embedding for the query
    2. Performs vector similarity search
    3. Returns most relevant document chunks with sources
    """
    # TODO: Implement semantic search with embeddings
    # This requires:
    # - Generating query embedding
    # - Vector similarity search using pgvector
    # - Returning chunks with metadata

    return {
        "message": "Semantic search not yet implemented",
        "query": query,
        "results": [],
    }
