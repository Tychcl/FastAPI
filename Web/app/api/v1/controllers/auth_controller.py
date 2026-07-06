from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from ..requests import SigninRequest, SignupRequest
from ..dependences import auth_service, role_service
from ..interfaces import IAuthService, IRoleService
from ...models import UserBase, UserRoleBase
from ..middlewares import auth_check, role_required
from ..validators import is_valid_username, is_valid_password
from typing import Optional

auth_controller = APIRouter(prefix="/auth")


@auth_controller.post("/signin")
async def signin(request: Request, 
                data: SigninRequest, 
                AuthService: IAuthService = Depends(auth_service)) -> JSONResponse:
    t: tuple[Optional[UserBase], Optional[JSONResponse]] = await AuthService.signin(data)
    user: Optional[UserBase] = t[0]
    response: JSONResponse = t[1]
    if user is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid login or password")
    return response

@role_required(2)
@auth_controller.post("/signup")
async def signup(request: Request, 
                data: SignupRequest, 
                AuthService: IAuthService = Depends(auth_service),
                RoleService: IRoleService = Depends(role_service),
                User: UserBase = Depends(auth_check)) -> JSONResponse:
    if not is_valid_username(data.username):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid username format")
    if not is_valid_password(data.password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid password format")
    if data.role_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "role required")
    role: Optional[UserRoleBase]= await RoleService.get_role_by_id(data.role_id)
    if role is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"role with id = {data.role_id} not exists")
    if User.role_id != 1 and role.id < User.role_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "you can't signup user with higher or equals role")
    new_user: Optional[UserBase] = await AuthService.signup(data)
    if new_user is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "user create error")
    return JSONResponse(content={"user": {"id": new_user.id, "username": new_user.username, "role_id": new_user.role_id, "role_name": role.name}}, status_code=200)

@auth_controller.post("/signout")
async def signout(request: Request, AuthService: IAuthService = Depends(auth_service)) -> RedirectResponse:
    return await AuthService.logout()