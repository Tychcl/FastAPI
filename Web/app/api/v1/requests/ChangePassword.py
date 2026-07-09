from pydantic import BaseModel

class ChangePassword(BaseModel):
    user_id: int
    new_password: str
    old_password: str