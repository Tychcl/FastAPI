from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import JSONResponse
from ..interfaces.IUserService import IUserService
from ..dependences import user_service
from ..middlewares import role_required, auth_check
from ...models import UserBase
from typing import Optional

user_controller = APIRouter()

@role_required(2)
@user_controller.post("/user/{id}")
async def get_user_by_id(request: Request, 
                         id: Optional[int] = None, 
                         UserService: IUserService = Depends(user_service),
                         user: Optional[UserBase] = Depends(auth_check)) -> JSONResponse:
    if id is None:
        return JSONResponse(content={"error": "id required"}, status_code=400)
    user = await UserService.get_user_by_id(id)
    return JSONResponse(content={"user": {"id": user.id, "username": user.username, "role_id": user.role_id, "role_name": user.role.name}}, status_code=200)