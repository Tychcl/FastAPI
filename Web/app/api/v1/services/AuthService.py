from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,  insert
from sqlalchemy.orm import selectinload
from ...models.user import UserBase
from ..interfaces import IAuthService, IPasswordHasherService, IUserService
from ..requests import SignupRequest, SigninRequest

class AuthService(IAuthService):
    def __init__(self, session: AsyncSession, hasher:IPasswordHasherService, user_service: IUserService):
        self.session = session
        self.hasher = hasher
        self.user_service = user_service

    async def signin(self, data: SigninRequest) -> UserBase | None: 
        sql = select(UserBase).options(selectinload(UserBase.role)).where(UserBase.username == data.username)
        result = await self.session.execute(sql)
        user = result.scalar_one_or_none()
        if user is not None and self.hasher.verify(data.password, user.password):
            return user
        return None
    
    async def signup(self, data: SignupRequest) -> UserBase | None:
        data.password = self.hasher.hash(data.password)
        user: UserBase = UserBase.from_signup_request(data)
        await self.user_service.create_user(user)
        return user
        