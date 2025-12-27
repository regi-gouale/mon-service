"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.availabilities import router as availabilities_router
from app.api.v1.routes.departments import router as departments_router
from app.api.v1.routes.plannings import router as plannings_router
from app.api.v1.routes.services import router as services_router
from app.api.v1.routes.users import router as users_router

router = APIRouter()

# Register auth routes
router.include_router(auth_router)

# Register user profile routes
router.include_router(users_router)

# Register department routes
router.include_router(departments_router)

# Register availability routes (nested under departments)
router.include_router(availabilities_router)

# Register service routes (nested under departments)
router.include_router(services_router)

# Register planning routes (nested under departments)
router.include_router(plannings_router)

# Additional routes will be registered here as they are implemented
