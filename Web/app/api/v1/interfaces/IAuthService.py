from abc import ABC, abstractmethod
from ..schemas import UserSignin, UserResponse, UserSignup
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Optional, Tuple

class IAuthService(ABC):
    @abstractmethod
    async def signin(self, data: UserSignin) -> Tuple[Optional[UserResponse], Optional[JSONResponse]]: pass
    
    @abstractmethod
    async def signup(self, data: UserSignup, pwd_hashed: bool = False) -> Optional[UserResponse]: pass
    
    @abstractmethod
    def logout(self) -> RedirectResponse: pass
    
    @abstractmethod
    async def change_password(self, id: int, new_password: str) -> bool: pass