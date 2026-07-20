from fastapi import APIRouter, Request, Depends, status, Query
from app.config import templates
from app.api.models import UserBase, UserRoleBase
from app.api.v1.dependences import role_service
from app.api.v1.interfaces import IRoleService, IUserService
from typing import Optional
from redis.asyncio import Redis
from app.config import auth_check, role_required, get_user
from app.api.v1.dependences import user_service
from fastapi.responses import RedirectResponse, JSONResponse
import json

pages_controller = APIRouter(tags=["web"])

@pages_controller.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="pages/index.html")

@pages_controller.get("/profile")
async def get_profile(request: Request,
                      id: Optional[int] = Query(default=None),
                      UserService: IUserService = Depends(user_service),
                      User: Optional[UserBase] = Depends(get_user)):
    context: dict = {'own': True}
    if id:
        other_user: Optional[UserBase] = await UserService.get_user_by(id=id, load_privacy=True)
        context['own'] = False
        if other_user:
            context['other_user'] = other_user.to_dict
    if User:
        return templates.TemplateResponse(request=request, name="pages/profile.html", context=context)
    else:
        return RedirectResponse("/authorize", status.HTTP_307_TEMPORARY_REDIRECT)
    
@pages_controller.get("/authorize")
async def get_authorize(request: Request):
    return templates.TemplateResponse(request=request, name="pages/auth/authorize.html")

@pages_controller.get("/authorize/email/verify")
async def get_email_verify(request: Request, token: Optional[str] = None):
    if token is None:
        return RedirectResponse("/profile")
    redis_client: Redis = request.app.state.redis
    data = await redis_client.get(f"email_verify:{token}")
    if not data:
        return RedirectResponse("/profile")
    context: dict = json.loads(data)
    return templates.TemplateResponse(request=request, name="pages/auth/verify.html", context=context)

@pages_controller.get("/password/change")
async def get_password_change(request: Request, token: Optional[str] = None):
    if token is None:
        return RedirectResponse("/profile")
    redis_client: Redis = request.app.state.redis
    data = await redis_client.get(f"password_forgot:{token}")
    if not data:
        return RedirectResponse("/profile")
    return templates.TemplateResponse(request=request, name="pages/auth/change_password.html")