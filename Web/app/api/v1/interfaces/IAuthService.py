from ...models.user import UserBase
from abc import ABC, abstractmethod
from ..requests import SignupRequest, SigninRequest
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Optional

class IAuthService(ABC):
    @abstractmethod
    async def signin(self, login: str, password: str) -> tuple[Optional[UserBase], Optional[JSONResponse]]: pass
    
    @abstractmethod
    async def signup(self, username: str, email: str, password: str, role_id: int, pwd_hashed: bool = False) -> Optional[UserBase]: pass
    
    @abstractmethod
    def logout(self) -> RedirectResponse: pass
    
    @abstractmethod
    async def change_password(self, id: int, new_password: str) -> bool: pass