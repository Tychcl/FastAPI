from ..interfaces import IRoleService
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...models import UserRoleBase
from typing import Optional

class RoleService(IRoleService):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_role_by_id(self, id: int) -> Optional[UserRoleBase]:
        sql = select(UserRoleBase).where(UserRoleBase.id == id)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()
    
    async def get_all_roles(self) -> list[UserRoleBase]:
        sql = select(UserRoleBase)
        result = await self.session.execute(sql)
        return result.scalar().all()