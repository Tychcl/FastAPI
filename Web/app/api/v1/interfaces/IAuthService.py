from ...models.user import UserBase
from abc import ABC, abstractmethod
from ..requests import SignupRequest, SigninRequest
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Optional

class IAuthService(ABC):
    @abstractmethod
    async def signin(self, data: SigninRequest) -> tuple[Optional[UserBase], Optional[JSONResponse]]: pass
    
    @abstractmethod
    async def signup(self, data: SignupRequest) -> Optional[UserBase]: pass
    
    @abstractmethod
    def logout(self) -> RedirectResponse: pass