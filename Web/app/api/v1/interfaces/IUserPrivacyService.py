from abc import ABC, abstractmethod
from typing import Optional
from app.api.models import UserPrivacyBase

class IUserPrivacyService(ABC):
    @abstractmethod
    async def get_privacy(self, user_id: int) -> Optional[UserPrivacyBase]: pass

    @abstractmethod
    async def create_default_privacy(self, user_id: int) -> UserPrivacyBase: pass

    @abstractmethod
    async def update_privacy(
        self,
        user_id: int,
        show_email: Optional[bool] = None,
        show_about: Optional[bool] = None
    ) -> UserPrivacyBase: pass