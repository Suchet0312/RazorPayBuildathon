from fastapi import APIRouter
from app.core.config import load_settings

router = APIRouter(tags=["health"])
settings = load_settings()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
    }
