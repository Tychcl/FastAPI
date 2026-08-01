from pydantic import BaseModel, EmailStr, field_validator, model_validator
from ...validators import is_valid_username, is_valid_password, is_valid_email
from typing import Optional, List
from .role import RoleResponse
from .privacy import PrivacyResponse

class UserSignup(BaseModel):
    ico: str = '👤'
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
    
class UserSignin(BaseModel):
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

class UserPasswordForgot(BaseModel):
    login: str
    
    @field_validator('login')
    def validate_login(cls, v):
        if not is_valid_username(v) and not is_valid_email(v):
            raise ValueError('Login must be username or email')
        return v

class UserPasswordChange(BaseModel):
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

class UserEmailChange(BaseModel):
    new_email: EmailStr
    
class UserEmailVerify(BaseModel):
    token: str
    code: int

class UserFindBy(BaseModel):
    id: Optional[int] = None, 
    username: Optional[str] = None, 
    email: Optional[str] = None

class UsersFind(BaseModel):
    ids: Optional[List[int]] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    role_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 25

class UserUpdate(BaseModel):
    ico: Optional[str] = None
    username: Optional[str] = None
    about: Optional[str] = None
    email: Optional[EmailStr] = None
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

class UserCreate(BaseModel):
    ico: str = '👤'
    username: str
    email: EmailStr
    password: str
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

class UserResponse(BaseModel):
    id: int
    ico: str
    username: str
    email: str
    about: Optional[str] = None
    role_id: int
    #role: Optional[RoleResponse] = None
    #privacy: Optional[PrivacyResponse] = None

    class Config:
        from_attributes = True