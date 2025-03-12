from fastapi import APIRouter

from src.users.routes.auth import oauth, router as auth_router
from src.users.routes.user_info import router as user_info_router

router = APIRouter()
router.include_router(user_info_router)
router.include_router(auth_router)
