from pydantic import BaseModel
from typing import Optional

class PrivacyUpdate(BaseModel):
    show_email: Optional[bool] = None
    show_about: Optional[bool] = None

class PrivacyResponse(BaseModel):
    user_id: int
    show_email: bool
    show_about: bool

    class Config:
        from_attributes = True