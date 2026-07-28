from abc import ABC, abstractmethod
from typing import Optional
from ..schemas import PrivacyResponse, PrivacyUpdate

class IPrivacyService(ABC):
    @abstractmethod
    async def get_privacy(self, user_id: int) -> Optional[PrivacyResponse]: pass

    @abstractmethod
    async def create_default_privacy(self, user_id: int) -> PrivacyResponse: pass

    @abstractmethod
    async def update_privacy(self, user_id: int, data: PrivacyUpdate) -> PrivacyResponse: pass