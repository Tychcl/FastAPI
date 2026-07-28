from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from ..schemas import UserCreate, UserResponse, UsersFind, UserUpdate

class IUserService(ABC):
    @abstractmethod
    async def create_user(self, data: UserCreate) -> UserResponse: pass
    
    @abstractmethod
    async def verify_password(self, user_id: int, password: str) -> bool: pass
    
    @abstractmethod
    async def get_user_by(self,
                        id: Optional[int] = None, 
                        username: Optional[str] = None, 
                        email: Optional[str] = None,
                        load_role: bool = True,
                        load_privacy: bool = False) -> Optional[UserResponse]: pass
    
    @abstractmethod
    async def find_users_by_any(self, data: UsersFind) -> Tuple[List[UserResponse], int, int]: pass
    
    @abstractmethod
    async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse: pass
    