from abc import ABC, abstractmethod
from ...models import UserRoleBase

class IRoleService(ABC):
    @abstractmethod
    async def get_role_by_id(self, id: int) -> UserRoleBase: pass
    
    @abstractmethod
    async def get_all_roles(self) -> list[UserRoleBase]: pass