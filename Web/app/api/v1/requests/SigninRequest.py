from pydantic import BaseModel

class SigninRequest(BaseModel):
    login: str
    password: str