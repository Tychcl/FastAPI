from ...models.user import UserBase
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

class IUserService(ABC):
    #create
    @abstractmethod
    async def create_user(self, user: UserBase) -> None: pass
    
    #read
    @abstractmethod
    async def get_user_by(self, 
                          id: Optional[int] = None, 
                          username: Optional[str] = None, 
                          email: Optional[str] = None, 
                          role_id: Optional[int] = None,
                          load_role: bool = True,
                          load_privacy: bool = False) -> Optional[UserBase]: pass
    
    @abstractmethod
    async def find_users_by_any(self, 
                                ids: Optional[List[int]] = None, 
                                username: Optional[str] = None, 
                                role_id: Optional[int] = None, 
                                page: int = 1, 
                                per_page: int = 25) -> Tuple[List[UserBase], int, int]: pass
    
    #update
    async def update_user(self, user_id: int, update_data: dict) -> UserBase: pass
    