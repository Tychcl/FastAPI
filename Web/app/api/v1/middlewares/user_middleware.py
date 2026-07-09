from fastapi import Request, Response
from ..interfaces import IJWTService, ICookieService
from ...models import UserBase
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.config import settings
from app.database import AsyncSessionLocal
from typing import Optional

async def user_middleware(request: Request, call_next):
    
    async def go_next(u: Optional[UserBase]):
        request.state.user = u
        response: Response = await call_next(request)
        if token_upd:
            CookieService.set_cookie(response, settings.JWT_STRING, token, settings.JWT_LIFETIME)
        return response
    
    CookieService: ICookieService = request.app.state.cookie_service
    JWTService: IJWTService = request.app.state.jwt_service
    
    token: Optional[str] = request.cookies.get(settings.JWT_STRING)
    token_upd: bool = False
    if token is None:
        refresh_token: Optional[str] = request.cookies.get(settings.REFRESH_STRING)
        if refresh_token is None:
            return await go_next(None)
        token = JWTService.refresh_access_token(refresh_token)
        if token is None:
            return await go_next(None)
        token_upd = True
    token_payload: Optional[dict] = JWTService.get_access_payload(token)
    if token_payload is None:
        token_upd = False
        return await go_next(None)
    user_id: Optional[int] = token_payload.get("user_id", None)
    async with AsyncSessionLocal() as session:
        stmt = select(UserBase).options(selectinload(UserBase.role)).where(UserBase.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
    return await go_next(user)    