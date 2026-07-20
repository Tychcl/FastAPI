# app/api/v1/services/UserPrivacyService.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Optional
from app.api.models import UserPrivacyBase
from app.api.v1.interfaces import IUserPrivacyService

class UserPrivacyService(IUserPrivacyService):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_privacy(self, user_id: int) -> Optional[UserPrivacyBase]:
        sql = select(UserPrivacyBase).where(UserPrivacyBase.user_id == user_id)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()

    async def create_default_privacy(self, user_id: int) -> UserPrivacyBase:
        existing = await self.get_privacy(user_id)
        if existing:
            return existing

        privacy = UserPrivacyBase(
            user_id=user_id,
            show_email=False,
            show_about=False
        )
        self.session.add(privacy)
        await self.session.commit()
        await self.session.refresh(privacy)
        return privacy

    async def update_privacy(
        self,
        user_id: int,
        show_email: Optional[bool] = None,
        show_about: Optional[bool] = None
    ) -> UserPrivacyBase:
        privacy = await self.get_privacy(user_id)
        if not privacy:
            privacy = UserPrivacyBase(
                user_id=user_id,
                show_email=show_email if show_email is not None else False,
                show_about=show_about if show_about is not None else False
            )
            self.session.add(privacy)
        else:
            if show_email is not None:
                privacy.show_email = show_email
            if show_about is not None:
                privacy.show_about = show_about

        await self.session.commit()
        await self.session.refresh(privacy)
        return privacy