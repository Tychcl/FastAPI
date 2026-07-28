from pydantic import BaseModel
from typing import Optional

class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True