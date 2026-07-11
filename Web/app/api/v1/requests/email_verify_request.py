from pydantic import BaseModel

class EmailVerifyRequest(BaseModel):
    code: int