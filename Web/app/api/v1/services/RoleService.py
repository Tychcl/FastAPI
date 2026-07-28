from ..interfaces import IRoleService
from ...models import UserRoleBase
from typing import Optional
from ..repositories import RoleRepo
from ..schemas import RoleResponse
from fastapi import HTTPException, status

class RoleService(IRoleService):
    def __init__(self, repo: RoleRepo):
        self.repo = repo
        
    async def get_role_by_id(self, id: int) -> Optional[RoleResponse]:
        role: Optional[UserRoleBase] = await self.repo.get(id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="role not found")
        return RoleResponse.model_validate(role)
    
    async def get_all_roles(self) -> list[RoleResponse]:
        roles: list[UserRoleBase] = await self.repo.get_all()
        return [RoleResponse.model_validate(role) for role in roles]