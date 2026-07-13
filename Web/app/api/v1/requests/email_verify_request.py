from pydantic import BaseModel

class EmailVerifyRequest(BaseModel):
    token: str
    code: int