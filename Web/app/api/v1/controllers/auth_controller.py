from fastapi import APIRouter, Request, Query, Depends, Response, HTTPException, status
from fastapi.responses import JSONResponse
from ..requests import SigninRequest, SignupRequest
from ..dependences import auth_service, cookie_service, jwt_service, role_service
from ..interfaces import IAuthService, ICookieService, IJWTService, IRoleService
from ...models import UserBase, UserRoleBase
from ..middlewares import auth_check, role_required
from sqlalchemy import inspect
from app.config import settings
from ..validators import is_valid_username, is_valid_password

auth_controller = APIRouter()


@auth_controller.post("/auth/signin")
async def signin(request: Request, 
                data: SigninRequest, 
                AuthService: IAuthService = Depends(auth_service),
                JWTService: IJWTService = Depends(jwt_service),
                CookieService: ICookieService = Depends(cookie_service)) -> JSONResponse:
    user: UserBase | None = await AuthService.signin(data)
    if user is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid login or password")
    response_data: dict = {c.key: getattr(user, c.key) for c in inspect(user).mapper.column_attrs}
    response_data['password'] = ""
    response_data['role_name'] = user.role.name
    response: Response = JSONResponse(content=response_data, status_code=200)
    user_data: dict = {"user_id": user.id, "user_role_id": user.role_id}
    access_token: str = JWTService.create_access_token(user_data)
    refresh_token: str = JWTService.create_refresh_token(user_data)
    CookieService.set_cookie(response, settings.JWT_STRING, access_token, settings.JWT_LIFETIME)
    CookieService.set_cookie(response, settings.REFRESH_STRING, refresh_token, settings.REFRESH_LIFETIME)
    return response

@role_required(2)
@auth_controller.post("/auth/signup")
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
    role: UserRoleBase | None = await RoleService.get_role_by_id(data.role_id)
    if role is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"role with id = {data.role_id} not exists")
    if User.role_id != 1 and role.id < User.role_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "you can't signup user with higher or equals role")
    new_user: UserBase | None = await AuthService.signup(data)
    if new_user is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "user create error")
    return JSONResponse(content={"user": {"id": new_user.id, "username": new_user.username, "role_id": new_user.role_id, "role_name": role.name}}, status_code=200)