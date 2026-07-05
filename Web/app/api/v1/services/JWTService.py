from app.config import settings
from jose import jwt
from datetime import datetime, timedelta, timezone
from ..interfaces import IJWTService
from typing import Optional

class JWTService(IJWTService):
    def __init__(self):
        data = settings.AUTH_DATA
        self.jwt_secret = data["JWT"]
        self.refresh_secret = data["REFRESH"]
        self.algorithm = data["ALGORITHM"]

    def create_access_token(self, data: dict) -> str:
        return self.encode_token(data, True)
    
    def create_refresh_token(self, data: dict) -> str:
        return self.encode_token(data, False)
    
    def get_access_payload(self, token: str) -> Optional[dict]:
        return self.decode_token(token, True)
    
    def get_refresh_payload(self, token: str) -> Optional[dict]:
        return self.decode_token(token, False)

    def encode_token(self, data: dict, is_access: bool = True) -> str:
        encode_data = data.copy()
        expire = datetime.now(timezone.utc)
        if is_access:
            expire = expire + timedelta(seconds=settings.JWT_LIFETIME)
        else:
            expire = expire + timedelta(seconds=settings.REFRESH_LIFETIME)
        encode_data.update({"exp": expire})
        secret = self.jwt_secret if is_access else self.refresh_secret
        return jwt.encode(encode_data, secret, algorithm=self.algorithm)
    
    def decode_token(self, token: str, is_access: bool = True) -> Optional[dict]:
        try:
            secret = self.jwt_secret if is_access else self.refresh_secret
            return jwt.decode(token, secret, algorithms=self.algorithm)
        except:
            return None
        
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        payload: Optional[dict] = self.decode_token(refresh_token, is_access=False)
        if payload is None:
            return None
        user_id: Optional[int] = payload.get("user_id")
        user_role_id: Optional[int] = payload.get("user_role_id")
        if user_id is None or user_role_id is None:
            return None
        new_access_token: str = self.create_access_token({"user_id": user_id, "user_role_id": user_role_id})
        return new_access_token
        