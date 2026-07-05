from fastapi import APIRouter, Request
from app.config import templates
from app.api.models import UserBase
from typing import Optional

pages_controller = APIRouter()

@pages_controller.get("/")
async def get_index(request: Request):
    context: dict = get_user_context(request)
    return templates.TemplateResponse(request=request, name="pages/index.html", context=context)

@pages_controller.get("/profile")
async def get_index(request: Request):
    context: dict = get_user_context(request)
    return templates.TemplateResponse(request=request, name="pages/profile.html", context=context)

def get_user_context(request: Request) -> dict:
    context: dict = {"user": None}
    user: Optional[UserBase] = request.state.user
    if user is not None:
        context['user'] = user.__repr__()
    return context