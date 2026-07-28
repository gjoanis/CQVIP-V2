from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
def get_public_settings():
    settings = get_settings()
    return {"environment": settings.environment, "anthropic_model": settings.anthropic_model}
