from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ...models.user import UserBase
from ..interfaces import IUserService

class UserService(IUserService):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_user(self, user: UserBase) -> None:
        exists: UserBase | None = await self.get_user_by_username(user.username)
        if exists is not None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"user {user.username} already exists")
        try:
            self.session.add(user)
        except:
            await self.session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "user create error")
        else:
            await self.session.commit()


    async def get_user_by_id(self, id: int) -> UserBase | None: 
        sql = select(UserBase).options(selectinload(UserBase.role)).where(UserBase.id == id)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> UserBase | None: 
        sql = select(UserBase).options(selectinload(UserBase.role)).where(UserBase.username == username)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()