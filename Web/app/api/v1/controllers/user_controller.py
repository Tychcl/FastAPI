from fastapi import APIRouter, Request, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..interfaces import IUserService, IRoleService, IUserPrivacyService, IPasswordHasherService
from ..dependences import user_service, role_service, privacy_service, password_hasher_service
from app.config import auth_check, role_required, get_authorized_user, clear_user_cache
from ...models import UserBase, UserRoleBase
from typing import Optional, List
from ..requests import UserUpdateRequest, PrivacyUpdateRequest

user_controller = APIRouter(prefix="/user", tags=["user"])

@user_controller.patch("/me", tags=['me'])
async def update_user(request: Request, 
                      data: UserUpdateRequest,
                      UserService: IUserService = Depends(user_service),
                      User: UserBase = Depends(get_authorized_user)) -> JSONResponse:
    verify = await UserService.verify_password(User.id, data.password)
    if not verify:
        raise HTTPException(400, "Wrong password")
    updated_user: UserBase = await UserService.update_user(User.id, data.model_dump(exclude_unset=True))
    await clear_user_cache(request)
    return_data: dict = updated_user.to_dict
    return_data.pop('password', None)
    return JSONResponse(content=return_data, status_code=200)

@user_controller.patch("/me/privacy", tags=['me'])
async def update_my_privacy(
    request: Request,
    data: PrivacyUpdateRequest,
    current_user: UserBase = Depends(auth_check),
    privacy_service: IUserPrivacyService = Depends(privacy_service)
):
    updated = await privacy_service.update_privacy(
        current_user.id,
        show_email=data.show_email,
        show_about=data.show_about
    )
    await clear_user_cache(request)
    return JSONResponse(content=updated.to_dict)

@role_required(UserRoleBase.ADMIN().id)
@user_controller.get("/find")
async def get_users_by_any(request: Request, 
                            ids: Optional[List[int]] = Query(None),
                            username: Optional[str] = Query(None),
                            email: Optional[str] = Query(None),
                            role_id: Optional[int] = Query(None),
                            page: int = Query(1, ge=1),
                            per_page: int = Query(25, ge=10, le=100),
                            UserService: IUserService = Depends(user_service),
                            user: Optional[UserBase] = Depends(auth_check)) -> JSONResponse:
    users, total_filtered, total_all = await UserService.find_users_by_any(ids, username, email, role_id, page, per_page)
    users_out = [u.to_dict for u in users]
    return JSONResponse(content={"users": users_out, "filtered": total_filtered, "all": total_all}, status_code=200)

@user_controller.get("/role", tags=["role"])
async def get_all_roles(request: Request, 
                            RoleService: IRoleService = Depends(role_service),
                            User: Optional[UserBase] = Depends(get_authorized_user)) -> JSONResponse:
    roles: List[UserRoleBase] = await RoleService.get_all_roles()
    roles_out = [r.to_dict for r in roles]
    return JSONResponse(content={"roles": roles_out}, status_code=200)

@user_controller.get("/role/{id}", tags=["role"])
async def get_role_by_id(request: Request, 
                            id: Optional[int] = None,
                            RoleService: IRoleService = Depends(role_service),
                            User: Optional[UserBase] = Depends(get_authorized_user)) -> JSONResponse:
    if id is None:
        return HTTPException(content={"error": "id required"}, status_code=400)
    role: UserRoleBase = await RoleService.get_role_by_id(id)
    return JSONResponse(content=role.to_dict, status_code=200)