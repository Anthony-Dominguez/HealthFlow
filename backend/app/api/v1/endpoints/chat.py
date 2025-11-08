"""Chat endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatRequest,
    ChatResponse,
)

router = APIRouter()


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session"""
    session = ChatSession(user_id=current_user.id, **session_data.model_dump())
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all chat sessions for the current user"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.last_message_at.desc())
    )
    sessions = result.scalars().all()
    return sessions


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
async def get_chat_messages(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all messages in a chat session"""
    # Verify session belongs to user
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id, ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
        )

    # Get messages
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    return messages


@router.post("/", response_model=ChatResponse)
async def send_chat_message(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a chat message and get AI response

    This endpoint:
    1. Creates or uses existing session
    2. Saves user message
    3. Performs RAG search for relevant context
    4. Generates AI response using context
    5. Saves AI response
    6. Returns response with sources
    """
    # Create or get session
    if chat_request.session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == chat_request.session_id,
                ChatSession.user_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
            )
    else:
        session = ChatSession(user_id=current_user.id, title="New Chat")
        db.add(session)
        await db.flush()

    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        user_id=current_user.id,
        role=MessageRole.USER,
        content=chat_request.message,
    )
    db.add(user_message)

    # TODO: Implement RAG search and AI response generation
    # For now, return a placeholder response
    assistant_response = ChatMessage(
        session_id=session.id,
        user_id=current_user.id,
        role=MessageRole.ASSISTANT,
        content="This is a placeholder response. RAG and AI integration will be implemented.",
        model_name="placeholder",
    )
    db.add(assistant_response)

    await db.commit()
    await db.refresh(assistant_response)

    return ChatResponse(
        session_id=session.id,
        message=ChatMessageResponse.model_validate(assistant_response),
        sources=[],
    )
