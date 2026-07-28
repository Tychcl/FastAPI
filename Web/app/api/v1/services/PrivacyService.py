from typing import Optional
from ...models import UserPrivacyBase
from ..interfaces import IPrivacyService
from ..repositories import PrivacyRepo
from ..schemas import PrivacyResponse, PrivacyUpdate

class PrivacyService(IPrivacyService):
    def __init__(self, repo: PrivacyRepo):
        self.repo = repo

    async def get_privacy(self, user_id: int) -> Optional[PrivacyResponse]:
        privacy: UserPrivacyBase = await self.repo.get(user_id)
        return PrivacyResponse.model_validate(privacy)

    async def create_default_privacy(self, user_id: int) -> PrivacyResponse:
        privacy: UserPrivacyBase = await self.repo.create(user_id)
        return PrivacyResponse.model_validate(privacy)

    async def update_privacy(self, user_id: int, data: PrivacyUpdate) -> PrivacyResponse:
        privacy: UserPrivacyBase = await self.repo.update(user_id, data)
        return PrivacyResponse.model_validate(privacy)