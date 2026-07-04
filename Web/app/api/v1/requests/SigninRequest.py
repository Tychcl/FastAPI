from pydantic import BaseModel

class SigninRequest(BaseModel):
    username: str
    password: str