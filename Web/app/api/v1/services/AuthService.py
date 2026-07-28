from fastapi.responses import JSONResponse, RedirectResponse
from ..repositories import UserRepo
from ...models.user import UserBase
from ..interfaces import IAuthService
from ...interfaces import IPasswordHasherService, IJWTService, ICookieService
from ..schemas import UserSignin, UserResponse, UserSignup
from app.config import settings
from typing import Optional, Tuple

class AuthService(IAuthService):
    def __init__(self, 
                 repo: UserRepo, 
                 hasher: IPasswordHasherService,
                 jwt_service: IJWTService,
                 cookie_service: ICookieService ):
        self.repo = repo
        self.hasher = hasher
        self.jwt_service = jwt_service
        self.cookie_service = cookie_service

    async def signin(self, data: UserSignin) -> Tuple[Optional[UserResponse], Optional[JSONResponse]]:
        user: Optional[UserBase] = await self.repo.get_by(email=data.login, username=data.login, load_role=True, load_privacy=True)
        if user is not None and self.hasher.verify(data.password, user.password):
            user_data: dict = user.to_dict
            access_token: str = self.jwt_service.create_access_token(user_data)
            refresh_token: str = self.jwt_service.create_refresh_token(user_data)
            response: JSONResponse = JSONResponse(content=user_data, status_code=200)
            self.cookie_service.set_cookie(response, settings.JWT_STRING, access_token, settings.JWT_LIFETIME)
            self.cookie_service.set_cookie(response, settings.REFRESH_STRING, refresh_token, settings.REFRESH_LIFETIME)
            return (UserResponse.model_validate(user), response)
        return (None, None)
    
    async def signup(self, data: UserSignup, pwd_hashed: bool = False) -> Optional[UserResponse]:
        data.password = self.hasher.hash(data.password) if not pwd_hashed else data.password
        user = await self.repo.create(data)
        return user
    
    async def logout(self) -> RedirectResponse:
        response: RedirectResponse = RedirectResponse(url="/", status_code=302)
        self.cookie_service.delete_cookie(response, settings.JWT_STRING)
        self.cookie_service.delete_cookie(response, settings.REFRESH_STRING)
        return response
    
    async def change_password(self, id: int, new_password: str) -> bool:
        try:
            user: UserBase = await self.repo.get_by(id=id)
            data: dict = {"password": self.hasher.hash(new_password)}
            await self.repo.update(user, data)
            return True
        except Exception as e:
            return False
            
    
    #async def change_password(self, id: int, new_password: str, old_password: str, current_user: UserBase) -> bool:
    #    if not is_valid_password(new_password):
    #        raise HTTPException(400, "Invalid new password format")
    #    sql = select(UserBase).where(UserBase.id == id)
    #    user = await self.session.scalar(sql)
    #    if not user:
    #        raise HTTPException(404, "User not found")
    #    if current_user.id != user.id and current_user.role_id >= user.role_id:
    #        raise HTTPException(404, "Access denied")
    #    elif current_user.id == user.id and not self.hasher.verify(old_password, user.password):
    #        raise HTTPException(400, "Old password is incorrect")
    #    else:
    #        pass #ВОТ ТУТ НАДО БЫ УТОЧНИТЬ МОГУТ ЛИ АДМИНЫ МЕНЯТЬ ПАРОЛИ ЛЮДЕЙ ЕСЛИ ОНИ ИХ ЗАБЫЛИ ИЛИ НАДО СДЕЛАТЬ ВОССТАОВЛЕНИЕ
    #    user.password = self.hasher.hash(new_password)
    #    await self.session.commit()
    #    return True