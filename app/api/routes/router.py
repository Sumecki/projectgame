from fastapi import APIRouter

from app.api.routes.health_controller import health_router
from app.api.routes.user_controller import user_router

router = APIRouter()

router.include_router(health_router)
router.include_router(user_router)
