from app.api.models.user import UserBase
from abc import ABC, abstractmethod

class IUserService(ABC):
    @abstractmethod
    async def create_user(self, user: UserBase) -> None: pass
    
    @abstractmethod
    async def get_user_by_id(self, id: int) -> UserBase | None: pass
    
    @abstractmethod
    async def get_user_by_username(self, username: str) -> UserBase | None: pass