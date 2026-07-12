from ...models.user import UserBase
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

class IUserService(ABC):
    @abstractmethod
    async def create_user(self, user: UserBase) -> None: pass
    
    @abstractmethod
    async def get_user_by(self, 
                          id: Optional[int] = None, 
                          username: Optional[str] = None, 
                          email: Optional[str] = None, 
                          role_id: Optional[int] = None) -> Optional[UserBase]: pass
    
    @abstractmethod
    async def find_users_by_any(self, 
                                ids: Optional[List[int]] = None, 
                                username: Optional[str] = None, 
                                role_id: Optional[int] = None, 
                                page: int = 1, 
                                per_page: int = 25) -> Tuple[List[UserBase], int, int]: pass
    