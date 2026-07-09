from fastapi import APIRouter, Request, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..interfaces import IUserService, IRoleService
from ..dependences import user_service, role_service
from app.config import auth_check, role_required
from ...models import UserBase, UserRoleBase
from typing import Optional, List, Tuple

user_controller = APIRouter(prefix="/user", tags=["user"])

@role_required(UserRoleBase.ADMIN().id)
@user_controller.get("/find")
async def get_users_by_any(request: Request, 
                            ids: Optional[List[int]] = Query(None),
                            username: Optional[str] = Query(None),
                            role_id: Optional[int] = Query(None),
                            page: int = Query(1, ge=1),
                            per_page: int = Query(25, ge=10, le=100),
                            UserService: IUserService = Depends(user_service),
                            user: Optional[UserBase] = Depends(auth_check)) -> JSONResponse:
    users, total_filtered, total_all = await UserService.find_users_by_any(ids, username, role_id, page, per_page)
    users_out = [u.to_dict for u in users]
    return JSONResponse(content={"users": users_out, "filtered": total_filtered, "all": total_all}, status_code=200)

@user_controller.get("/role", tags=["role"])
async def get_all_roles(request: Request, 
                            RoleService: IRoleService = Depends(role_service),
                            user: Optional[UserBase] = Depends(auth_check)) -> JSONResponse:
    roles: List[UserRoleBase] = await RoleService.get_all_roles()
    roles_out = [r.to_dict for r in roles]
    return JSONResponse(content={"roles": roles_out}, status_code=200)

@user_controller.get("/role/{id}", tags=["role"])
async def get_role_by_id(request: Request, 
                            id: Optional[int] = None,
                            RoleService: IRoleService = Depends(role_service),
                            user: Optional[UserBase] = Depends(auth_check)) -> JSONResponse:
    if id is None:
        return HTTPException(content={"error": "id required"}, status_code=400)
    role: UserRoleBase = await RoleService.get_role_by_id(id)
    return JSONResponse(content=role.to_dict, status_code=200)

@role_required(UserRoleBase.ADMIN().id)
@user_controller.get("/{id}")
async def get_user_by_id(request: Request, 
                         id: Optional[int] = None, 
                         UserService: IUserService = Depends(user_service),
                         user: Optional[UserBase] = Depends(auth_check)) -> JSONResponse:
    if id is None:
        return HTTPException(content={"error": "id required"}, status_code=400)
    user = await UserService.get_user_by_id(id)
    return JSONResponse(content={"user": {"id": user.id, "username": user.username, "role_id": user.role_id, "role_name": user.role.name}}, status_code=200)