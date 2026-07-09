from fastapi import APIRouter, Request, Depends
from app.config import templates
from app.api.models import UserBase, UserRoleBase
from app.api.v1.dependences import role_service
from app.api.v1.interfaces import IRoleService
from typing import Optional

pages_controller = APIRouter()

@pages_controller.get("/")
async def get_index(request: Request):
    #context: dict = get_user_context(request)
    return templates.TemplateResponse(request=request, name="pages/index.html")

@pages_controller.get("/profile")
async def get_index(request: Request, 
                    RoleService: IRoleService = Depends(role_service)):
    context: dict = {}
    if request.state.user:
        roles = await RoleService.get_all_roles()
        context['roles'] = [r.to_dict for r in roles]
    return templates.TemplateResponse(request=request, name="pages/profile.html", context=context)

def get_user_context(request: Request) -> dict:
    context: dict = {"user": None}
    user: Optional[UserBase] = request.state.user
    if user is not None:
        context['user'] = user.__repr__()
    return context