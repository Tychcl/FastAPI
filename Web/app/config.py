from fastapi.templating import Jinja2Templates
import os
import ssl
import logging
from pydantic_settings import BaseSettings
from fastapi import HTTPException, status, Request
from typing import Optional
from .api.models import UserBase
from functools import wraps

async def get_authorized_user(request: Request) -> Optional[UserBase]:
    try:
        user: Optional[UserBase] = request.state.user
    except AttributeError:
        user = None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "unauthorized")
    return user

async def get_user(request: Request) -> Optional[UserBase]:
    try:
        user: Optional[UserBase] = request.state.user
    except AttributeError:
        user = None
    return user

async def auth_check(request: Request) -> UserBase:
    user: Optional[UserBase] = await get_authorized_user(request)
    endpoint = request.scope.get("endpoint")
    if endpoint is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "endpoint is none")
    role_needed: Optional[int] = getattr(endpoint, "_role_required", None)
    if role_needed is not None and role_needed < user.role_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, {"user": {"id": user.id, "role_id": user.role_id},"role_needed": role_needed, "msg": "access denied"})
    return user
    
def role_required(role_required: int):
    def decorator(func):
        func._role_required = role_required
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class Settings(BaseSettings):
    BASE_URL: str
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    #Redis
    REDIS_PASSWORD: str
    REDIS_USER: str
    REDIS_USER_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int
    #DataBase
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    #JWT
    JWT_LIFETIME: int
    JWT_STRING: str
    JWT_SECRET: str
    REFRESH_LIFETIME: int
    REFRESH_STRING: str
    REFRESH_SECRET: str
    ALGORITHM_SECRET: str
    #SESSION
    SESSION_SECRET: str
    #SMTP
    SMTP_MAIL: str
    SMTP_MAIL_PWD: str

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def AUTH_DATA(self) -> dict:
        return {"JWT": self.JWT_SECRET, "REFRESH": self.REFRESH_SECRET, "ALGORITHM": self.ALGORITHM_SECRET}
    
    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_USER}:{self.REDIS_USER_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"

ssl_options = {"ssl_cert_reqs": ssl.CERT_NONE}
settings = Settings()
templates = Jinja2Templates(directory=os.path.join(settings.BASE_DIR, "web/templates"))
logger = logging.getLogger(__name__)

templates.context_processors.append(lambda request: {"user": request.state.user.__repr__() if request.state.user else None})