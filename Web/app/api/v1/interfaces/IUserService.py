from ...models.user import UserBase
from abc import ABC, abstractmethod
from typing import Optional

class IUserService(ABC):
    @abstractmethod
    async def create_user(self, user: UserBase) -> None: pass
    
    @abstractmethod
    async def get_user_by_id(self, id: int) -> Optional[UserBase]: pass
    
    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[UserBase]: pass