from pydantic import BaseModel

class PasswordChangeRequest(BaseModel):
    token: str
    password: str
    confirm: str