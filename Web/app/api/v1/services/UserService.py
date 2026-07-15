from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ...models import UserBase, UserPrivacyBase
from ..interfaces import IUserService
from sqlalchemy import select, func, or_
from typing import Optional, List, Tuple

class UserService(IUserService):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_user(self, user: UserBase) -> None:
        exists_user: Optional[UserBase] = await self.get_user_by(username=user.username, email=user.email)
        if exists_user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"user with that username or email already exists")
        try:
            self.session.add(user)
            self.session.flush()
            privacy = UserPrivacyBase(user_id=user.id)
            self.session.add(privacy)
        except:
            await self.session.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "user create error")
        else:
            await self.session.commit()
    
    async def get_user_by(self, id: Optional[int] = None, username: Optional[str] = None, email: Optional[str] = None, role_id: Optional[int] = None) -> Optional[UserBase]:
        conditions: list = []
        if id:
            conditions.append(UserBase.id == id)
        if username:
            conditions.append(UserBase.username == username)
        if email:
            conditions.append(UserBase.email == email)
        if role_id:
            conditions.append(UserBase.role_id == role_id)
        sql = select(UserBase).options(selectinload(UserBase.role)).where(or_(*conditions))
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()

    async def find_users_by_any(
        self,
        ids: Optional[List[int]] = None,
        username: Optional[str] = None,
        email: Optional[str] = None,
        role_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 25
    ) -> Tuple[List[UserBase], int, int]:
        sql = select(UserBase)
        conditions = self._build_conditions(ids, username, email, role_id)
        if conditions:
            sql = sql.where(*conditions)
        sql = sql.options(selectinload(UserBase.role))
        sql = sql.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(sql)
        count: int = await self.count_users_by_filters()
        count_filter: int = count
        if conditions:
            count_filter = await self.count_users_by_filters(conditions)
        return result.scalars().all(), count_filter, count
    
    async def count_users_by_filters(self, conditions: Optional[list] = None) -> int:
        sql = select(func.count()).select_from(UserBase)
        if conditions:
            sql = sql.where(*conditions)
        return await self.session.scalar(sql) or 0
    
    def _build_conditions(self, 
                          ids: Optional[List[int]] = None, 
                          username: Optional[str] = None, 
                          email: Optional[str] = None, 
                          role_id: Optional[int] = None):
        conditions = []
        if ids is not None and ids.count > 0:
            conditions.append(UserBase.id.in_(ids))
        if username is not None:
            conditions.append(UserBase.username.ilike(f'%{username}%'))
        if email is not None:
            conditions.append(UserBase.email.ilike(f'%{email}%'))
        if role_id is not None:
            conditions.append(UserBase.role_id == role_id)
        return conditions