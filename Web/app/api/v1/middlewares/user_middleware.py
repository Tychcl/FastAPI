from fastapi import Request, Response, status
from ..interfaces import IJWTService, ICookieService
from ...models import UserBase, UserRoleBase, UserPrivacyBase
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.config import settings, dict_to_user
from app.database import AsyncSessionLocal
from typing import Optional
from redis.asyncio import Redis
from fastapi.responses import JSONResponse
import json

async def user_middleware(request: Request, call_next):
    jwt_service: IJWTService = request.app.state.jwt_service
    cookie_service: ICookieService = request.app.state.cookie_service
    user = None
    token_upd = False
    access_token = request.cookies.get(settings.JWT_STRING)
    refresh_token = request.cookies.get(settings.REFRESH_STRING)
    payload = None
    #Обновление access token
    if refresh_token and not access_token:
        access_token = jwt_service.refresh_access_token(refresh_token)
        if access_token:
            token_upd = True
            payload = jwt_service.get_access_payload(access_token)
    elif access_token and refresh_token:
        payload = jwt_service.get_access_payload(access_token)
        if not payload:
            access_token = jwt_service.refresh_access_token(refresh_token)
            if access_token:
                token_upd = True
                payload = jwt_service.get_access_payload(access_token)
    #загрузка пользователя
    if payload:
        user_id: Optional[int] = payload.get("id", None)
        if user_id:
            redis_client: Redis = request.app.state.redis
            cached = await redis_client.get(f"user:{access_token}")
            if cached:
                user_data = json.loads(cached)
                user = dict_to_user(user_data)
            else:
                user = await get_user_by_id(user_id)
                if user:
                    await redis_client.setex(f"user:{access_token}", settings.JWT_LIFETIME, json.dumps(user.to_dict))
    
    request.state.user = user
    response = await call_next(request)
    if token_upd and access_token:
        cookie_service.set_cookie(response, settings.JWT_STRING, access_token, settings.JWT_LIFETIME)
    return response

async def get_user_by_id(id: Optional[int] = None) -> Optional[UserBase]:
    if id:
        async with AsyncSessionLocal() as session:
            sql = select(UserBase).options(selectinload(UserBase.role), 
                                           selectinload(UserBase.privacy)).where(UserBase.id == id)
            result = await session.execute(sql)
            return result.scalar_one_or_none()
    return None        