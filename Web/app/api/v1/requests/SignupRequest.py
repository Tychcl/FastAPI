from pydantic import BaseModel, EmailStr, field_validator, model_validator
from ..validators import is_valid_username, is_valid_password

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm: str
    role_id: int = 3

    @field_validator('username')
    def validate_username(cls, v):
        if not is_valid_username(v):
            raise ValueError('Username must contain only Latin letters')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if not is_valid_password(v):
            raise ValueError('Invalid password format')
        return v

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.confirm:
            raise ValueError('Passwords do not match')
        return self