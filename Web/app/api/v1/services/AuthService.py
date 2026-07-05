from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,  insert
from sqlalchemy.orm import selectinload
from ...models.user import UserBase
from ..interfaces import IAuthService, IPasswordHasherService, IUserService, IJWTService, ICookieService
from ..requests import SignupRequest, SigninRequest
from app.config import settings
from typing import Optional

class AuthService(IAuthService):
    def __init__(self, session: AsyncSession, 
                 hasher:IPasswordHasherService, 
                 user_service: IUserService,
                 jwt_service: IJWTService,
                 cookie_service: ICookieService ):
        self.session = session
        self.hasher = hasher
        self.user_service = user_service
        self.jwt_service = jwt_service
        self.cookie_service = cookie_service

    async def signin(self, data: SigninRequest) -> tuple[Optional[UserBase], Optional[JSONResponse]]: 
        sql = select(UserBase).options(selectinload(UserBase.role)).where(UserBase.username == data.username)
        result = await self.session.execute(sql)
        user: Optional[UserBase] = result.scalar_one_or_none()
        if user is not None and self.hasher.verify(data.password, user.password):
            user_data: dict = user.__repr__()
            access_token: str = self.jwt_service.create_access_token(user_data)
            refresh_token: str = self.jwt_service.create_refresh_token(user_data)
            response: JSONResponse = JSONResponse(content=user_data, status_code=200)
            self.cookie_service.set_cookie(response, settings.JWT_STRING, access_token, settings.JWT_LIFETIME)
            self.cookie_service.set_cookie(response, settings.REFRESH_STRING, refresh_token, settings.REFRESH_LIFETIME)
            return (user, response)
        return (None, None)
    
    async def signup(self, data: SignupRequest) -> Optional[UserBase]:
        data.password = self.hasher.hash(data.password)
        user: UserBase = UserBase.from_signup_request(data)
        await self.user_service.create_user(user)
        return user