from .interfaces import IUserService, IAuthService, IRoleService, IPrivacyService
from ..interfaces import IJWTService, IPasswordHasherService, ICookieService
from .services import UserService, AuthService, RoleService, PrivacyService
from ..services import JWTService, PasswordHasherService, CookieService
from .repositories import UserRepo, RoleRepo, PrivacyRepo
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.database import get_context

#repo
async def user_repo(session: AsyncSession = Depends(get_context)) -> UserRepo:
    return UserRepo(session=session)

async def role_repo(session: AsyncSession = Depends(get_context)) -> RoleRepo:
    return RoleRepo(session=session)

async def privacy_repo(session: AsyncSession = Depends(get_context)) -> PrivacyRepo:
    return PrivacyRepo(session=session)

#regular services
async def jwt_service() -> IJWTService:
    return JWTService()

async def password_hasher_service() -> IPasswordHasherService:
    return PasswordHasherService()

async def cookie_service() -> ICookieService:
    return CookieService()

#services
async def auth_service(repo: UserRepo = Depends(user_repo),
                       hasher: IPasswordHasherService = Depends(password_hasher_service),
                       jwt: IJWTService = Depends(jwt_service),
                       cook: ICookieService = Depends(cookie_service)) -> IAuthService:
    return AuthService(repo=repo, hasher=hasher, jwt_service=jwt, cookie_service=cook)

async def user_service(user_repo: UserRepo = Depends(user_repo),
                       privacy_repo: PrivacyRepo = Depends(privacy_repo),
                       hasher: IPasswordHasherService = Depends(password_hasher_service)) -> IUserService:
    return UserService(user_repo=user_repo, privacy_repo=privacy_repo, hasher=hasher)

async def role_service(repo: RoleRepo = Depends(role_repo)) -> IRoleService:
    return RoleService(repo=repo)

async def privacy_service(repo: PrivacyRepo = Depends(privacy_repo)) -> IPrivacyService:
    return PrivacyService(repo=repo)