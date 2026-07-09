from fastapi import APIRouter
from app.web.controllers import pages_controller, admin_controller

web_router = APIRouter()

web_router.include_router(pages_controller)
web_router.include_router(admin_controller)