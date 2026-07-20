from .interfaces import IJWTService, IPasswordHasherService, IUserService, IAuthService, ICookieService, IRoleService, IUserPrivacyService
from .services import JWTService, PasswordHasherService, UserService, AuthService, CookieService, RoleService, UserPrivacyService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.database import get_context

async def jwt_service() -> IJWTService:
    return JWTService()

async def password_hasher_service() -> IPasswordHasherService:
    return PasswordHasherService()

async def user_service(session: AsyncSession = Depends(get_context),
                       hasher: IPasswordHasherService = Depends(password_hasher_service)) -> IUserService:
    return UserService(session, hasher)

async def role_service(session: AsyncSession = Depends(get_context)) -> IRoleService:
    return RoleService(session)

async def privacy_service(session: AsyncSession = Depends(get_context)) -> IUserPrivacyService:
    return UserPrivacyService(session)

async def cookie_service() -> ICookieService:
    return CookieService()

async def auth_service(session: AsyncSession = Depends(get_context), 
                       hasher: IPasswordHasherService = Depends(password_hasher_service),
                       user_service: IUserService = Depends(user_service),
                       jwt_service: IJWTService = Depends(jwt_service),
                       cookie_service: ICookieService = Depends(cookie_service)) -> IAuthService:
    return AuthService(session, hasher, user_service, jwt_service, cookie_service)