from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ...models.user import UserBase
from ..interfaces import IUserService
from sqlalchemy import select, func
from typing import Optional, List, Tuple

class UserService(IUserService):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_user(self, user: UserBase) -> None:
        exists: Optional[UserBase] = await self.get_user_by_username(user.username)
        if exists is not None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"user {user.username} already exists")
        try:
            self.session.add(user)
        except:
            await self.session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "user create error")
        else:
            await self.session.commit()

    async def get_user_by_id(self, id: int) -> Optional[UserBase]: 
        sql = select(UserBase).options(selectinload(UserBase.role)).where(UserBase.id == id)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[UserBase]: 
        sql = select(UserBase).options(selectinload(UserBase.role)).where(UserBase.username == username)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()
    
    async def count_all_users(self) -> int:
        sql = select(func.count()).select_from(UserBase)
        return await self.session.scalar(sql) or 0

    async def count_users_by_filters(
        self,
        ids: Optional[List[int]] = None,
        username: Optional[str] = None,
        role_id: Optional[int] = None,
    ) -> int:
        sql = select(func.count()).select_from(UserBase)
        conditions = self._build_conditions(ids, username, role_id)
        if conditions:
            sql = sql.where(*conditions)
        return await self.session.scalar(sql) or 0

    def _build_conditions(self, ids, username, role_id):
        conditions = []
        if ids is not None:
            conditions.append(UserBase.id.in_(ids))
        if username is not None:
            conditions.append(UserBase.username.ilike(f'%{username}%'))  # или ilike для частичного поиска
        if role_id is not None:
            conditions.append(UserBase.role_id == role_id)
        return conditions

    async def find_users_by_any(
        self,
        ids: Optional[List[int]] = None,
        username: Optional[str] = None,
        role_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> List[UserBase]:
        sql = select(UserBase)
        conditions = self._build_conditions(ids, username, role_id)
        if conditions:
            sql = sql.where(*conditions)
        #sql = sql.options(selectinload(UserBase.role))
        sql = sql.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(sql)
        return result.scalars().all()