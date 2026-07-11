from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from ..requests import SigninRequest, SignupRequest, ChangePassword, EmailVerifyRequest
from ..dependences import auth_service, role_service, user_service
from ..interfaces import IAuthService, IRoleService, IPasswordHasherService, IUserService
from ...models import UserBase, UserRoleBase
from app.config import auth_check, role_required, get_user
from ..validators import is_valid_username, is_valid_password, is_valid_email
from app.celery import celery_app
from typing import Optional
import secrets
import json
from redis.asyncio import Redis
from random import randint
import asyncio
from celery.result import AsyncResult

auth_controller = APIRouter(prefix="/auth", tags=["auth"])

@auth_controller.post("/signin")
async def signin(request: Request, 
                data: SigninRequest, 
                AuthService: IAuthService = Depends(auth_service)) -> JSONResponse:
    t: tuple[Optional[UserBase], Optional[JSONResponse]] = await AuthService.signin(data.login, data.password)
    user: Optional[UserBase] = t[0]
    response: JSONResponse = t[1]
    if user is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid login or password")
    return response

@auth_controller.post("/signup")
async def signup(request: Request, 
                data: SignupRequest,
                RoleService: IRoleService = Depends(role_service),
                UserService: IUserService = Depends(user_service)) -> JSONResponse:
    if not is_valid_username(data.username):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid username format")
    if not is_valid_email(data.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid email format")
    if not is_valid_password(data.password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid password format")
    if data.password != data.confirm:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "password confirmation error")
    if data.role_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "role required")
    role: Optional[UserRoleBase]= await RoleService.get_role_by_id(data.role_id)
    if role is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"role with id = {data.role_id} not exists")
    exists: bool = await UserService.check_user_exists(username=data.username, email=data.email)
    if exists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"user with that username or email already exists")
    hash_service: IPasswordHasherService = request.app.state.hash_service
    code: int = randint(1000,9999)
    user_data: dict = {"username": data.username, "email": data.email, "password": hash_service.hash(data.password),"role_id": data.role_id}
    redis_client: Redis = request.app.state.redis
    request.session["email"] = data.email
    task: AsyncResult = celery_app.send_task(
        'send_verify_email_code',
        args=[data.email, code],
        queue='celery'
    )
    try:
        success = await asyncio.to_thread(task.get, timeout=30)
    except TimeoutError:
        raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "Email service timeout")
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Email sending failed: {str(e)}")
    if not success:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to send verification email")
    await redis_client.setex(f"temp_user:{code}", 600, json.dumps(user_data))
    return JSONResponse(content={"msg": f"verification code send to {data.email}"}, status_code=status.HTTP_200_OK)#RedirectResponse("/authorize/email/verify")

@auth_controller.post("/signout")
async def signout(request: Request, AuthService: IAuthService = Depends(auth_service)) -> RedirectResponse:
    return await AuthService.logout()

@auth_controller.post("/email/verify")
async def email_verify(request: Request,
                       data: EmailVerifyRequest,
                       AuthService: IAuthService = Depends(auth_service)) -> RedirectResponse:
    email: Optional[str] = request.session["email"]
    if email is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "email not found in session")
    key = f"temp_user:{data.code}"
    redis_client: Redis = request.app.state.redis
    data = await redis_client.get(key)
    if data:
        user_data: dict = json.loads(data)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "signup out of time, try again")
    if email != user_data.get("email", None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "wrong email")
    username: Optional[str] = user_data.get("username", None)
    password: Optional[str] = user_data.get("password", None)
    role_id: Optional[int] = user_data.get("role_id", None)
    if username is None or password is None or role_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "fields is none")
    new_user: Optional[UserBase] = await AuthService.signup(username, email, password, role_id, True)
    if new_user is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "user create error")
    return RedirectResponse("/profile")

#@auth_controller.post("/password/change")
#async def password_change(request: Request, 
#                          data: ChangePassword, 
#                          AuthService: IAuthService = Depends(auth_service),
#                          User: Optional[UserBase] = Depends(get_user)) -> JSONResponse:
#    if data.user_id is None or data.new_password is None or data.old_password is None:
#        raise HTTPException(status.HTTP_400_BAD_REQUEST, "All fields required")
#    result: bool = await AuthService.change_password(data.user_id, data.new_password, data.old_password, User)
#    return JSONResponse(content=result, status_code=status.HTTP_200_OK)

#@auth_controller.post("/telegram")
#async def telegram(request: Request):
#    path_params = request.path_params
#    query_params = dict(request.query_params)
#    headers = dict(request.headers)
#    cookies = dict(request.cookies)
#    body = await request.body()
#    return JSONResponse(content={
#        "path_params": path_params,
#        "query_params": query_params,
#        "headers": headers,
#        "cookies": cookies,
#        "body": body.decode() if body else None,
#    }, status_code=status.HTTP_200_OK)