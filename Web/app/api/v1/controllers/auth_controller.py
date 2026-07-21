from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from ..requests import SigninRequest, SignupRequest, PasswordForgotRequest, EmailVerifyRequest, PasswordChangeRequest, EmailChangeRequest
from ..dependences import auth_service, role_service, user_service
from ..interfaces import IAuthService, IRoleService, IPasswordHasherService, IUserService
from ...models import UserBase, UserRoleBase
from app.config import auth_check, role_required, get_user, get_authorized_user, settings, clear_user_cache
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
    data.role_id = UserRoleBase.USER().id
    role: Optional[UserRoleBase]= await RoleService.get_role_by_id(data.role_id)
    if role is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"role with id = {data.role_id} not exists")
    exists: Optional[UserBase] = await UserService.get_user_by(username=data.username, email=data.email)
    if exists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"user with that username or email already exists")
    hash_service: IPasswordHasherService = request.app.state.hash_service
    code: int = randint(1000,9999)
    token: str = secrets.token_urlsafe(16)
    user_data: dict = {"username": data.username, "email": data.email, "password": hash_service.hash(data.password),"role_id": data.role_id, "code": code}
    redis_client: Redis = request.app.state.redis
    request.session["email"] = data.email
    try:
        celery_app.send_task(
            'send_verify_email_code',
            args=[data.email, code],
            queue='celery'
        )
    except:
        raise HTTPException(500, "Email sending failed")
    await redis_client.setex(f"email_verify:{token}", 600, json.dumps(user_data))
    return JSONResponse(content={"msg": f"verification code send to {data.email}", "token": token}, status_code=status.HTTP_200_OK)#RedirectResponse("/authorize/email/verify")

@auth_controller.post("/signout")
async def signout(request: Request, AuthService: IAuthService = Depends(auth_service)) -> JSONResponse:
    redis_client: Redis = request.app.state.redis
    await redis_client.delete(f"user:{request.cookies.get(settings.JWT_STRING)}")
    return await AuthService.logout()

@auth_controller.post("/password/forgot", tags=["password"])
async def password_forgot(request: Request,
                          data: PasswordForgotRequest,
                          UserService: IUserService = Depends(user_service)) -> JSONResponse:
    user: Optional[UserBase] = await UserService.get_user_by(username=data.login, email=data.login, load_privacy=True)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user with that login not found")
    user_data: dict = user.to_dict
    token: str = secrets.token_urlsafe(16)
    try:
        celery_app.send_task(
            'send_password_forgot_link',
            args=[user.email, token],
            queue='celery'
        )
    except:
        raise HTTPException(500, "Email sending failed")
    redis_client: Redis = request.app.state.redis
    await redis_client.setex(f"password_forgot:{token}", 600, json.dumps(user_data))
    return JSONResponse(content={"message": "password change link sended to your email"}, status_code=status.HTTP_200_OK)

@auth_controller.post("/password/change", tags=["password"])
async def password_change(request: Request,
                          data: PasswordChangeRequest,
                          User: Optional[UserBase] = Depends(get_user),
                          AuthService: IAuthService = Depends(auth_service)) -> JSONResponse:
    if not is_valid_password(data.password):
        raise HTTPException(400, "Invalid new password format")
    if data.password != data.confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="password confirmation error")
    key = f"password_forgot:{data.token}"
    redis_client: Redis = request.app.state.redis
    redis_data = await redis_client.get(key)
    if redis_data is None and User is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="signup out of time, try again")
    user_data: dict = json.loads(redis_data)
    id: Optional[int] = user_data.get("id", None) or User.id
    if id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User data not found")
    await AuthService.change_password(id, data.password)
    await redis_client.delete(key)
    return JSONResponse(content={"msg": "password changed"}, status_code=status.HTTP_200_OK)

@auth_controller.post("/email/change", tags=["email"])
async def email_change(request: Request,
                       data: EmailChangeRequest,
                       User: UserBase = Depends(get_authorized_user),
                       UserService: IUserService = Depends(user_service)) -> JSONResponse:
    if User.email == data.new_email:
        raise HTTPException(400, "This is your current email")
    exists: Optional[UserBase] = await UserService.get_user_by(email=data.new_email)
    if exists:
        raise HTTPException(400, "Email already taken")
    redis_client: Redis = request.app.state.redis
    token: str = secrets.token_urlsafe(16)
    code: int = randint(1000,9999)
    redis_data: dict = {"email": data.new_email, "code": code}
    request.session["email"] = data.new_email
    await redis_client.setex(f"email_verify:{token}", 600, json.dumps(redis_data))
    try:
        celery_app.send_task(
            'send_verify_email_code',
            args=[data.new_email, code],
            queue='celery'
        )
    except:
        raise HTTPException(500, "Email change code sending failed")
    try:
        celery_app.send_task(
            'send_email_change_link',
            args=[User.email, token],
            queue='celery'
        )
    except:
        raise HTTPException(500, "Email change link sending failed")
    return JSONResponse(content={"msg": f"Change link send to {User.email}\nVerification code send to {data.new_email}", "token": token}, status_code=status.HTTP_200_OK)

@auth_controller.post("/email/verify", tags=["email"])
async def email_verify(request: Request,
                       data: EmailVerifyRequest,
                       AuthService: IAuthService = Depends(auth_service),
                       UserService: IUserService = Depends(user_service),
                       User: Optional[UserBase] = Depends(get_user)) -> JSONResponse:
    email: Optional[str] = request.session["email"]
    if email is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "email not found in session")
    key = f"email_verify:{data.token}"
    redis_client: Redis = request.app.state.redis
    r_data = await redis_client.get(key)
    if r_data:
        redis_data: dict = json.loads(r_data)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Email verify out of time, try again")
    if redis_data.get("code", None) is None:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "code data error")
    if data.code != redis_data.get("code", None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "wrong code")
    if email != redis_data.get("email", None):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "wrong email")
    
    if User is None:
        username: Optional[str] = redis_data.get("username", None)
        password: Optional[str] = redis_data.get("password", None)
        role_id: Optional[int] = redis_data.get("role_id", None)
        if username is None or password is None or role_id is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "fields is none")
        new_user: Optional[UserBase] = await AuthService.signup(username, email, password, role_id, True)
        if new_user is None:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "user create error")
    else:
        await UserService.update_user(User.id, {"email": email})
        await clear_user_cache(request)
    
    await redis_client.delete(key)
    request.session.pop("email")
    return JSONResponse(content={"msg": "email verified"}, status_code=status.HTTP_200_OK)