from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from ..validators import is_valid_username, is_valid_password

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    about: Optional[str] = None
    password: Optional[str] = None
    new_password: Optional[str] = None

    @field_validator('username')
    def validate_username(cls, v):
        if v is not None and not is_valid_username(v):
            raise ValueError('Username must contain only Latin letters')
        return v

    @field_validator('new_password')
    def validate_new_password(cls, v):
        if v is not None and not is_valid_password(v):
            raise ValueError('Invalid new password format')
        return v