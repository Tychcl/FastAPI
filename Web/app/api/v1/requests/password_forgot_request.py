from pydantic import BaseModel, field_validator
from ..validators import is_valid_username, is_valid_email

class PasswordForgotRequest(BaseModel):
    login: str
    
    @field_validator('login')
    def validate_login(cls, v):
        if not is_valid_username(v) and not is_valid_email(v):
            raise ValueError('Login must be username or email')
        return v