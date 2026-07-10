from fastapi import Request, Response, status
from ..interfaces import IJWTService, ICookieService
from ...models import UserBase
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.config import settings
from app.database import AsyncSessionLocal
from typing import Optional
from fastapi.responses import JSONResponse

async def user_middleware(request: Request, call_next):
    
    jwt_service: IJWTService = request.app.state.jwt_service
    cookie_service: ICookieService = request.app.state.cookie_service
    
    user: Optional[UserBase] = None
    token_upd = False
    access_token:str = request.cookies.get(settings.JWT_STRING)
    refresh_token:str = request.cookies.get(settings.REFRESH_STRING)
    
    if refresh_token is not None and access_token is None:
        access_token = jwt_service.refresh_access_token(refresh_token)
        token_upd = access_token is not None
    
    if access_token is not None and refresh_token is not None:
        payload: Optional[dict] = jwt_service.get_access_payload(access_token)
        if payload:
            user_id: Optional[int] = payload.get("user_id", None)
            if user_id:
                async with AsyncSessionLocal() as session:
                    sql = select(UserBase).options(selectinload(UserBase.role)).where(UserBase.id == user_id)
                    result = await session.execute(sql)
                    user = result.scalar_one_or_none()
    
    request.state.user = user
    response: Response = await call_next(request)
    if token_upd:
        cookie_service.set_cookie(response, settings.JWT_STRING, access_token, settings.JWT_LIFETIME)
    return response