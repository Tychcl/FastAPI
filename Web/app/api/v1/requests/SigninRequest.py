from pydantic import BaseModel, field_validator
from ..validators import is_valid_username, is_valid_email, is_valid_password

class SigninRequest(BaseModel):
    login: str
    password: str
    
    @field_validator('login')
    def validate_login(cls, v):
        if not is_valid_username(v) and not is_valid_email(v):
            raise ValueError('Login must be username or email')
        return v
    
    @field_validator('password')
    def validate_password(cls, v):
        if not is_valid_password(v):
            raise ValueError('Invalid password format')
        return v