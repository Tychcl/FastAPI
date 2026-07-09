from ...models.user import UserBase
from abc import ABC, abstractmethod
from ..requests import SignupRequest, SigninRequest
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Optional

class IAuthService(ABC):
    @abstractmethod
    async def signin(self, username: str, password: str) -> tuple[Optional[UserBase], Optional[JSONResponse]]: pass
    
    @abstractmethod
    async def signup(self, username: str, password: str, role_id: int) -> Optional[UserBase]: pass
    
    @abstractmethod
    def logout(self) -> RedirectResponse: pass
    
    @abstractmethod
    async def change_password(self, id: int, new_password: str, old_password, current_user: UserBase): pass