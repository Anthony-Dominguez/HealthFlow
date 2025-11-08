"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.schemas.user import UserLogin, TokenResponse, UserCreate, UserResponse
from app.core.config import settings
from supabase import create_client, Client

router = APIRouter()


def get_supabase_client() -> Client:
    """Get Supabase client"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user with Supabase Auth

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user
    """
    try:
        supabase = get_supabase_client()

        # Register user with Supabase Auth
        auth_response = supabase.auth.sign_up(
            {
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name,
                        "phone_number": user_data.phone_number,
                    }
                },
            }
        )

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user",
            )

        return UserResponse(
            id=auth_response.user.id,
            email=auth_response.user.email,
            full_name=user_data.full_name,
            date_of_birth=user_data.date_of_birth,
            phone_number=user_data.phone_number,
            profile_data=user_data.profile_data or {},
            preferences=user_data.preferences or {},
            created_at=auth_response.user.created_at,
            updated_at=auth_response.user.updated_at or auth_response.user.created_at,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
):
    """
    Login with email and password using Supabase Auth

    Args:
        credentials: Login credentials

    Returns:
        Access and refresh tokens
    """
    try:
        supabase = get_supabase_client()

        # Login with Supabase
        auth_response = supabase.auth.sign_in_with_password(
            {"email": credentials.email, "password": credentials.password}
        )

        if not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        return TokenResponse(
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token,
            token_type="bearer",
            expires_in=auth_response.session.expires_in,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """
    Refresh access token

    Args:
        refresh_token: Refresh token

    Returns:
        New access and refresh tokens
    """
    try:
        supabase = get_supabase_client()

        auth_response = supabase.auth.refresh_session(refresh_token)

        if not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        return TokenResponse(
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token,
            token_type="bearer",
            expires_in=auth_response.session.expires_in,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout")
async def logout():
    """
    Logout user (client should delete tokens)

    Returns:
        Success message
    """
    return {"message": "Logged out successfully"}
