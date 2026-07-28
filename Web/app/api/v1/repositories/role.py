from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from ...models import UserRoleBase

class RoleRepo():
    def __init__(self, session: AsyncSession):
        self.session = session
    
    #read
    async def get(self, id: int) -> Optional[UserRoleBase]:
        sql = select(UserRoleBase).where(UserRoleBase.id == id)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()
    
    async def get_all(self) -> list[UserRoleBase]:
        sql = select(UserRoleBase)
        result = await self.session.execute(sql)
        return result.scalars().all() 