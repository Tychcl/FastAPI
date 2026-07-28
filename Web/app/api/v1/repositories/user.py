from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple, Union
from ...models import UserBase
from ..schemas import UserSignup, UsersFind, UserCreate, UserFindBy

class UserRepo():
    def __init__(self, session: AsyncSession):
        self.session = session
    
    #create
    async def create(self, data: Union[UserSignup, UserCreate]) -> UserBase:
        user: UserBase = UserBase(**data.model_dump())
        self.session.add(user)
        await self.session.commit()
        return user
    
    #read
    async def get_by(self,
                    id: Optional[int] = None,
                    username: Optional[str] = None,
                    email: Optional[str] = None,
                    load_role: bool = True, 
                    load_privacy: bool = False) -> Optional[UserBase]:
        opt: list = []
        if load_role:
            opt.append(selectinload(UserBase.role))
        if load_privacy:
            opt.append(selectinload(UserBase.privacy))
        conditions: list = []
        if id:
            conditions.append(UserBase.id == id)
        if username:
            conditions.append(UserBase.username == username)
        if email:
            conditions.append(UserBase.email == email)
        sql = select(UserBase)
        if len(opt) > 0:
            sql = sql.options(*opt)
        if len(conditions) > 0:
            sql = sql.where(or_(*conditions))
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()
    
    async def find_users_by_any(self, filters: UsersFind) -> Tuple[List[UserBase], int, int]:
        conditions = self._build_conditions(filters)
        sql = select(UserBase)
        if conditions:
            sql = sql.where(*conditions)
        sql = sql.offset((filters.page - 1) * filters.per_page).limit(filters.per_page)
        result = await self.session.execute(sql)
        users = result.scalars().all()
        total_all = await self.count_users_by_filters()
        total_filtered = await self.count_users_by_filters(conditions)
        return users, total_filtered, total_all
    
    def _build_conditions(self, filters: UsersFind):
            conditions = []
            if filters.ids is not None and len(filters.ids) > 0:
                conditions.append(UserBase.id.in_(filters.ids))
            if filters.username is not None:
                conditions.append(UserBase.username.ilike(f'%{filters.username}%'))
            if filters.email is not None:
                conditions.append(UserBase.email.ilike(f'%{filters.email}%'))
            if filters.role_id is not None:
                conditions.append(UserBase.role_id == filters.role_id)
            return conditions
        
    async def count_users_by_filters(self, conditions: Optional[list] = None) -> int:
        sql = select(func.count()).select_from(UserBase)
        if conditions:
            sql = sql.where(*conditions)
        return await self.session.scalar(sql) or 0
    
    #update
    async def update(self, user: UserBase, update_data: dict) -> UserBase:
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.session.commit()
        #await self.session.refresh(user, attribute_names=['role', 'privacy'])
        #user = await self.get_by(id=user.id, load_role=True, load_privacy=True)
        return user
    
    #delete
    async def delete(self, id: int) -> bool:
        sql = delete(UserBase).where(UserBase.id == id)
        try:
            await self.session.execute(sql)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            return False
        