"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router

router = APIRouter()

# Register auth routes
router.include_router(auth_router)

# Additional routes will be registered here as they are implemented
