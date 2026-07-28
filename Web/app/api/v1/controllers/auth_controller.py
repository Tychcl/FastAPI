from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from ..dependences import auth_service, role_service, user_service
from ..interfaces import IAuthService, IRoleService, IUserService
from ...interfaces import IPasswordHasherService
from ...models import UserBase
from app.config import get_user, get_authorized_user, settings, clear_user_cache
from typing import Optional
import secrets
import json
from redis.asyncio import Redis
from random import randint
from celery import Celery
from ...validators import is_valid_password
from ..schemas import UserSignin, UserSignup, UserEmailVerify, UserResponse, RoleResponse, UserPasswordForgot, UserPasswordChange, UserEmailChange, UserUpdate

auth_controller = APIRouter(prefix="/auth", tags=["auth"])

@auth_controller.post("/signin")
async def signin(request: Request, 
                data: UserSignin, 
                AuthService: IAuthService = Depends(auth_service)) -> JSONResponse:
    user, response = await AuthService.signin(data)
    if user is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid login or password")
    return response

@auth_controller.post("/signup")
async def signup(request: Request, 
                data: UserSignup,
                RoleService: IRoleService = Depends(role_service),
                UserService: IUserService = Depends(user_service)) -> JSONResponse:
    role: Optional[RoleResponse]= await RoleService.get_role_by_id(data.role_id)
    if role is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"role with id = {data.role_id} not exists")
    exists: Optional[UserResponse] = await UserService.get_user_by(username=data.username, email=data.email)
    if exists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"user with that username or email already exists")
    hash_service: IPasswordHasherService = request.app.state.hash_service
    code: int = randint(1000,9999)
    token: str = secrets.token_urlsafe(16)
    user_data: dict = {"username": data.username, "email": data.email, "password": hash_service.hash(data.password),"role_id": data.role_id, "code": code}
    redis_client: Redis = request.app.state.redis
    request.session["email"] = data.email
    try:
        celery_app: Celery = request.app.state.celery
        celery_app.send_task(
            'send_verify_email_code',
            args=[data.email, code],
            queue='celery'
        )
    except:
        raise HTTPException(500, "Email sending failed")
    await redis_client.setex(f"email_verify:{token}", 600, json.dumps(user_data))
    return JSONResponse(content={"msg": f"verification code send to {data.email}", "token": token}, status_code=status.HTTP_200_OK)

@auth_controller.post("/signout")
async def signout(request: Request, AuthService: IAuthService = Depends(auth_service)) -> JSONResponse:
    redis_client: Redis = request.app.state.redis
    await redis_client.delete(f"user:{request.cookies.get(settings.JWT_STRING)}")
    return await AuthService.logout()

@auth_controller.post("/password/forgot", tags=["password"])
async def password_forgot(request: Request,
                          data: UserPasswordForgot,
                          UserService: IUserService = Depends(user_service)) -> JSONResponse:
    user: Optional[UserResponse] = await UserService.get_user_by(username=data.login, email=data.login, load_privacy=True)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user with that login not found")
    token: str = secrets.token_urlsafe(16)
    try:
        celery_app: Celery = request.app.state.celery
        celery_app.send_task(
            'send_password_forgot_link',
            args=[user.email, token],
            queue='celery'
        )
    except:
        raise HTTPException(500, "Email sending failed")
    redis_client: Redis = request.app.state.redis
    await redis_client.setex(f"password_forgot:{token}", 600, json.dumps(user.model_dump()))
    return JSONResponse(content={"message": "password change link sended to your email"}, status_code=status.HTTP_200_OK)

@auth_controller.post("/password/change", tags=["password"])
async def password_change(request: Request,
                          data: UserPasswordChange,
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
                       data: UserEmailChange,
                       User: UserBase = Depends(get_authorized_user),
                       UserService: IUserService = Depends(user_service)) -> JSONResponse:
    if User.email == data.new_email:
        raise HTTPException(400, "This is your current email")
    exists: Optional[UserResponse] = await UserService.get_user_by(email=data.new_email)
    if exists:
        raise HTTPException(400, "Email already taken")
    redis_client: Redis = request.app.state.redis
    token: str = secrets.token_urlsafe(16)
    code: int = randint(1000,9999)
    redis_data: dict = {"email": data.new_email, "code": code}
    request.session["email"] = data.new_email
    await redis_client.setex(f"email_verify:{token}", 600, json.dumps(redis_data))
    try:
        celery_app: Celery = request.app.state.celery
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
                       data: UserEmailVerify,
                       AuthService: IAuthService = Depends(auth_service),
                       UserService: IUserService = Depends(user_service),
                       User: Optional[UserBase] = Depends(get_user)) -> JSONResponse:
    email: Optional[str] = request.session["email"]
    if email is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "email not found in session")
    
    key = f"email_verify:{data.token}"
    redis_client: Redis = request.app.state.redis
    redis_data = await redis_client.get(key)
    if redis_data is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "verification expired, try again")
    
    payload: dict = json.loads(redis_data)
    if payload.get("code") != data.code:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "wrong code")
    if payload.get("email") != email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "email mismatch")
    
    if User is None:
        user_data = {"username": payload["username"],
                    "email": payload["email"],
                    "password": payload["password"],
                    "role_id": payload["role_id"]}
        us: UserSignup = UserSignup(username=user_data["username"],
                        email=user_data["email"],
                        password=user_data["password"],
                        confirm=user_data["password"],
                        role_id=user_data["role_id"])
        new_user = await AuthService.signup(us, True)
        if not new_user:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "user creation failed")
    else:
        uu: UserUpdate = UserUpdate(email=email)
        await UserService.update_user(User.id, uu)
        await clear_user_cache(request)
    
    await redis_client.delete(key)
    request.session.pop("email", None)
    return JSONResponse(content={"msg": "email verified"}, status_code=status.HTTP_200_OK)