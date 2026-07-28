from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from ..interfaces import IUserService, IRoleService, IPrivacyService
from ..dependences import user_service, role_service, privacy_service
from app.config import auth_check, role_required, get_authorized_user, clear_user_cache
from ...models import UserBase, UserRoleBase
from typing import Optional, List
from ..schemas import UserUpdate, PrivacyUpdate, UserResponse, PrivacyResponse, UsersFind, RoleResponse

user_controller = APIRouter(prefix="/user", tags=["user"])

@user_controller.patch("/me", tags=['me'])
async def update_user(request: Request, 
                      data: UserUpdate,
                      UserService: IUserService = Depends(user_service),
                      User: UserBase = Depends(get_authorized_user)) -> JSONResponse:
    verify = await UserService.verify_password(User.id, data.password)
    if not verify:
        raise HTTPException(400, "Wrong password")
    updated_user: UserResponse = await UserService.update_user(User.id, data)
    await clear_user_cache(request)
    return JSONResponse(content=updated_user.model_dump(exclude={'password'}), status_code=200)

@user_controller.patch("/me/privacy", tags=['me'])
async def update_my_privacy(request: Request,
                            data: PrivacyUpdate,
                            User: UserBase = Depends(auth_check),
                            privacy_service: IPrivacyService = Depends(privacy_service))-> JSONResponse:
    updated: PrivacyResponse = await privacy_service.update_privacy(User.id, data)
    await clear_user_cache(request)
    return JSONResponse(content=updated.model_dump(), status_code=status.HTTP_200_OK)

@role_required(UserRoleBase.ADMIN().id)
@user_controller.post("/find")
async def get_users_by_any(request: Request, data: UsersFind,
                            UserService: IUserService = Depends(user_service),
                            user: Optional[UserBase] = Depends(auth_check)) -> JSONResponse:
    users, total_filtered, total_all = await UserService.find_users_by_any(data)
    users_out = [u.model_dump() for u in users]
    return JSONResponse(content={"users": users_out, "filtered": total_filtered, "all": total_all}, status_code=200)

@user_controller.get("/role", tags=["role"])
async def get_all_roles(request: Request, 
                        RoleService: IRoleService = Depends(role_service),
                        User: Optional[UserBase] = Depends(get_authorized_user)) -> JSONResponse:
    roles: List[RoleResponse] = await RoleService.get_all_roles()
    roles_out = [r.model_dump() for r in roles]
    return JSONResponse(content={"roles": roles_out}, status_code=200)

@user_controller.get("/role/{id}", tags=["role"])
async def get_role_by_id(id: Optional[int] = None,
                        RoleService: IRoleService = Depends(role_service),
                        User: Optional[UserBase] = Depends(get_authorized_user)) -> JSONResponse:
    if id is None:
        return HTTPException(content={"error": "id required"}, status_code=400)
    role: Optional[RoleResponse] = await RoleService.get_role_by_id(id)
    return JSONResponse(content=role.model_dump(), status_code=200)