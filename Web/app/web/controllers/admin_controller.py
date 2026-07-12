from fastapi import APIRouter, Request, Depends
from app.config import templates
from app.api.models import UserBase, UserRoleBase
from app.api.v1.dependences import role_service
from app.api.v1.interfaces import IRoleService
from typing import Optional
from app.config import auth_check, role_required

admin_controller = APIRouter(prefix="/admin", tags=["web"])

@role_required(UserRoleBase.ADMIN().id)
@admin_controller.get("/panel")
async def get_index(request: Request, RoleService: IRoleService = Depends(role_service), user: UserBase  = Depends(auth_check)):
    context: dict = {}
    if user:
        roles = await RoleService.get_all_roles()
        context['roles'] = [r.to_dict for r in roles]
    return templates.TemplateResponse(request=request, name="pages/admin/panel.html", context=context)