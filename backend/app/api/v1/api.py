"""API v1 router"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    documents,
    medical_entities,
    timeline,
    chat,
    search,
)

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(
    medical_entities.router, prefix="/medical-entities", tags=["Medical Entities"]
)
api_router.include_router(timeline.router, prefix="/timeline", tags=["Timeline"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
