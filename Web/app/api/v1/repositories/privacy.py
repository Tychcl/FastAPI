from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from ...models import UserPrivacyBase
from ..schemas import PrivacyUpdate

class PrivacyRepo():
    def __init__(self, session: AsyncSession):
        self.session = session
    
    #create
    async def create(self, user_id: int) -> UserPrivacyBase:
        existing = await self.get(user_id)
        if existing:
            return existing
        privacy = UserPrivacyBase(
            user_id=user_id,
            show_email=False,
            show_about=True
        )
        self.session.add(privacy)
        await self.session.commit()
        await self.session.refresh(privacy)
        return privacy
    
    #read
    async def get(self, user_id: int) -> Optional[UserPrivacyBase]:
        sql = select(UserPrivacyBase).where(UserPrivacyBase.user_id == user_id)
        result = await self.session.execute(sql)
        return result.scalar_one_or_none()
    
    #update
    async def update(self, user_id: int, data: PrivacyUpdate) -> UserPrivacyBase:
        privacy = await self.get(user_id)
        upd_data = data.model_dump(exclude_unset=True)
        if not privacy:
            privacy = UserPrivacyBase(user_id=user_id)
            self.session.add(privacy)
            if upd_data:
                for field, value in upd_data.items():
                    setattr(privacy, field, value)
        elif upd_data:
            for field, value in upd_data.items():
                setattr(privacy, field, value)
        await self.session.commit()
        await self.session.refresh(privacy)
        return privacy
        
        
        