from fastapi import APIRouter, Request, Depends, status
from app.config import templates
from app.api.models import UserBase, UserRoleBase
from app.api.v1.dependences import role_service
from app.api.v1.interfaces import IRoleService
from typing import Optional
from app.config import auth_check, role_required, get_user
from fastapi.responses import RedirectResponse

pages_controller = APIRouter()

@pages_controller.get("/")
async def get_index(request: Request):
    #context: dict = get_user_context(request)
    return templates.TemplateResponse(request=request, name="pages/index.html")

@pages_controller.get("/profile")
async def get_index(request: Request, User: Optional[UserBase] = Depends(get_user)):
    context: dict = {}
    if User:
        return templates.TemplateResponse(request=request, name="pages/profile.html", context=context)
    else:
        return RedirectResponse("/authorize", status.HTTP_307_TEMPORARY_REDIRECT)
    
@pages_controller.get("/authorize")
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="pages/auth/authorize.html")

@pages_controller.get("/authorize/email/verify")
async def get_index(request: Request):
    context: dict = {"email": request.session["email"]}
    return templates.TemplateResponse(request=request, name="pages/auth/verify.html", context=context)

def get_user_context(request: Request) -> dict:
    context: dict = {"user": None}
    user: Optional[UserBase] = request.state.user
    if user is not None:
        context['user'] = user.__repr__()
    return context