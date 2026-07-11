from pydantic import BaseModel

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    role_id: int
    confirm: str