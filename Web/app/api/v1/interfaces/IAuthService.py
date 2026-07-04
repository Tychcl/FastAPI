from ...models.user import UserBase
from abc import ABC, abstractmethod
from ..requests import SignupRequest, SigninRequest

class IAuthService(ABC):
    @abstractmethod
    async def signin(self, data: SigninRequest) -> UserBase | None: pass
    
    @abstractmethod
    async def signup(self, data: SignupRequest) -> UserBase | None: pass