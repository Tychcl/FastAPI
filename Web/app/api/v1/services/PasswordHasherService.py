from passlib.context import CryptContext
from app.api.v1.interfaces import IPasswordHasherService

class PasswordHasherService(IPasswordHasherService):
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify(self, password: str, hash: str) -> bool:
        return self.pwd_context.verify(password, hash)