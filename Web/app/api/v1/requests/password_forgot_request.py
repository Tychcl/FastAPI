from pydantic import BaseModel

class PasswordForgotRequest(BaseModel):
    login: str