from fastapi import HTTPException, status
from ...models import UserBase
from ..interfaces import IUserService
from ...interfaces import IPasswordHasherService
from typing import Optional, List, Tuple
from ..schemas import UserCreate, UserResponse, UsersFind, UserUpdate
from ..repositories import UserRepo, PrivacyRepo

class UserService(IUserService):
    def __init__(self, user_repo: UserRepo, 
                privacy_repo: PrivacyRepo, 
                hasher: IPasswordHasherService):
        self.user_repo = user_repo
        self.privacy_repo = privacy_repo
        self.hasher = hasher
    
    #create
    async def create_user(self, data: UserCreate) -> UserResponse:
        exists_user: Optional[UserBase] = await self.user_repo.get_by(username=data.username, email=data.email, load_role=False)
        if exists_user.email == data.email:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Email already taken")
        if exists_user.username == data.username:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Username already taken")
        try:
            data.password = self.hasher.hash(data.password)
            u: UserBase = await self.user_repo.create(data)
            await self.privacy_repo.create(u.id)
            return UserResponse.model_validate(u)
        except:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "user create error")
    
    #read
    async def verify_password(self, user_id: int, password: str) -> bool:
        user: UserBase = await self.user_repo.get_by(id=user_id)
        hashed_password = user.password
        if hashed_password is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return self.hasher.verify(password, hashed_password)
        
    async def get_user_by(self,
                        id: Optional[int] = None, 
                        username: Optional[str] = None, 
                        email: Optional[str] = None,
                        load_role: bool = True,
                        load_privacy: bool = False) -> Optional[UserResponse]:
        user: Optional[UserBase] = await self.user_repo.get_by(id=id, username=username, email=email, load_role=load_role, load_privacy=load_privacy)
        if user:
            return UserResponse.model_validate(user)
        return None

    async def find_users_by_any(self, data: UsersFind) -> Tuple[List[UserResponse], int, int]:
        users, f, a = await self.user_repo.find_users_by_any(data)
        return [UserResponse.model_validate(user) for user in users], f, a
    
    #update
    async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse:
        user_orm: Optional[UserBase] = await self.user_repo.get_by(id=user_id, load_role=True, load_privacy=True)
        if user_orm is None:
            raise HTTPException(404, "User not found")
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        un: Optional[str] = update_data.get('username', None)
        e: Optional[str] = update_data.get('email', None)
        exists_user: Optional[UserBase] = await self.user_repo.get_by(username=un, email=e)
        if exists_user:
            if exists_user.email == e:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Email already taken")
            if exists_user.username == un:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Username already taken")
        update_data.pop('password', None)
        if 'new_password' in update_data:
            update_data['password'] = self.hasher.hash(update_data['new_password'])
            update_data.pop('new_password', None)
        updated_orm = await self.user_repo.update(user_orm, update_data)
        return UserResponse.model_validate(updated_orm)