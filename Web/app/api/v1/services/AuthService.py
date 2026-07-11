from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, or_
from sqlalchemy.orm import selectinload
from ...models.user import UserBase
from ..interfaces import IAuthService, IPasswordHasherService, IUserService, IJWTService, ICookieService
from ..requests import SignupRequest, SigninRequest
from app.config import settings
from typing import Optional
from ..validators import is_valid_password, is_valid_email
from fastapi import HTTPException, status

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

    async def signin(self, login: str, password: str) -> tuple[Optional[UserBase], Optional[JSONResponse]]:
        sql = select(UserBase).options(selectinload(UserBase.role)).where(or_(UserBase.email == login, UserBase.username == login))
        result = await self.session.execute(sql)
        user: Optional[UserBase] = result.scalar_one_or_none()
        if user is not None and self.hasher.verify(password, user.password):
            user_data: dict = user.__repr__()
            access_token: str = self.jwt_service.create_access_token(user_data)
            refresh_token: str = self.jwt_service.create_refresh_token(user_data)
            response: JSONResponse = JSONResponse(content=user_data, status_code=200)
            self.cookie_service.set_cookie(response, settings.JWT_STRING, access_token, settings.JWT_LIFETIME)
            self.cookie_service.set_cookie(response, settings.REFRESH_STRING, refresh_token, settings.REFRESH_LIFETIME)
            return (user, response)
        return (None, None)
    
    async def signup(self, username: str, email: str, password: str, role_id: int, pwd_hashed: bool = False) -> Optional[UserBase]:
        password: str = self.hasher.hash(password) if not pwd_hashed else password
        user: UserBase = UserBase(username=username, email=email, password=password, role_id=role_id)
        await self.user_service.create_user(user)
        return user
    
    async def logout(self) -> RedirectResponse:
        response: RedirectResponse = RedirectResponse(url="/", status_code=302)
        self.cookie_service.delete_cookie(response, settings.JWT_STRING)
        self.cookie_service.delete_cookie(response, settings.REFRESH_STRING)
        return response
    
    async def change_password(self, id: int, new_password: str, old_password: str, current_user: UserBase) -> bool:
        if not is_valid_password(new_password):
            raise HTTPException(400, "Invalid new password format")
        sql = select(UserBase).where(UserBase.id == id)
        user = await self.session.scalar(sql)
        if not user:
            raise HTTPException(404, "User not found")
        if current_user.id != user.id and current_user.role_id >= user.role_id:
            raise HTTPException(404, "Access denied")
        elif current_user.id == user.id and not self.hasher.verify(old_password, user.password):
            raise HTTPException(400, "Old password is incorrect")
        else:
            pass #ВОТ ТУТ НАДО БЫ УТОЧНИТЬ МОГУТ ЛИ АДМИНЫ МЕНЯТЬ ПАРОЛИ ЛЮДЕЙ ЕСЛИ ОНИ ИХ ЗАБЫЛИ ИЛИ НАДО СДЕЛАТЬ ВОССТАОВЛЕНИЕ
        user.password = self.hasher.hash(new_password)
        await self.session.commit()
        return True