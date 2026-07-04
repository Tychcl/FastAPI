from fastapi import APIRouter
from app.web.controllers.pages import pages_controller

web_router = APIRouter()

web_router.include_router(pages_controller)