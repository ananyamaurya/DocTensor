from fastapi import APIRouter
from doctensor.api.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health():
    """Returns 200 OK when the API is reachable."""
    from doctensor.api.config import get_settings
    return HealthResponse(version=get_settings().app_version)
