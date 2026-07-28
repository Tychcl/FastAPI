from abc import ABC, abstractmethod
from ...models import UserRoleBase
from typing import Optional
from ..schemas import RoleResponse

class IRoleService(ABC):
    @abstractmethod
    async def get_role_by_id(self, id: int) -> Optional[RoleResponse]: pass
    
    @abstractmethod
    async def get_all_roles(self) -> list[RoleResponse]: pass