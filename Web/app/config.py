from fastapi.templating import Jinja2Templates
import os
import logging
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    JWT_LIFETIME: int
    JWT_STRING: str
    JWT_SECRET: str
    REFRESH_LIFETIME: int
    REFRESH_STRING: str
    REFRESH_SECRET: str
    ALGORITHM_SECRET: str

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def AUTH_DATA(self) -> dict:
        return {"JWT": self.JWT_SECRET, "REFRESH": self.REFRESH_SECRET, "ALGORITHM": self.ALGORITHM_SECRET}

settings = Settings()
templates = Jinja2Templates(directory=os.path.join(settings.BASE_DIR, "web/templates"))
logger = logging.getLogger(__name__)