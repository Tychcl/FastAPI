from pydantic import BaseModel, field_validator, model_validator
from ..validators import is_valid_password

class PasswordChangeRequest(BaseModel):
    token: str
    password: str
    confirm: str
    
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