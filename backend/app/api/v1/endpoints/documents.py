"""Document endpoints"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentType, ProcessingStatus
from app.schemas.document import DocumentResponse, DocumentList, DocumentUpload
from app.schemas.common import PaginatedResponse
from app.core.config import settings
from supabase import create_client

router = APIRouter()


@router.post("/upload", response_model=DocumentUpload, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a document

    This endpoint uploads a file to Supabase Storage and creates a document record.
    The document will be queued for processing (OCR, entity extraction, etc.)
    """
    # Validate file size
    if file.size and file.size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Validate MIME type
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} is not supported",
        )

    try:
        # Upload to Supabase Storage
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        file_path = f"{current_user.id}/{file.filename}"

        # Read file content
        content = await file.read()

        # Upload to Supabase Storage
        supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
            file_path, content, {"content-type": file.content_type}
        )

        # Create document record
        document = Document(
            user_id=current_user.id,
            file_name=file.filename,
            storage_path=file_path,
            mime_type=file.content_type,
            file_size=len(content),
            document_type=document_type,
            processing_status=ProcessingStatus.PENDING,
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        # TODO: Queue document for processing (Celery task)

        return DocumentUpload(
            document_id=document.id,
            message="Document uploaded successfully and queued for processing",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}",
        )


@router.get("/", response_model=PaginatedResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    document_type: DocumentType = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all documents for the current user"""
    query = select(Document).where(Document.user_id == current_user.id)

    if document_type:
        query = query.where(Document.document_type == document_type)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    # Get paginated results
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(Document.uploaded_at.desc())
    result = await db.execute(query)
    documents = result.scalars().all()

    return PaginatedResponse.create(
        items=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific document"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id, Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id, Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # Delete from storage
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).remove([document.storage_path])
    except Exception as e:
        # Log error but continue with database deletion
        pass

    await db.delete(document)
    await db.commit()
