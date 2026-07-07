from fastapi import APIRouter
from .controllers import auth_controller, user_controller

api_router = APIRouter(prefix="/api/v1", tags=["v1"])
api_router.include_router(auth_controller)
api_router.include_router(user_controller)