from abc import ABC, abstractmethod
from typing import Optional

class IJWTService(ABC):
    @abstractmethod
    def create_access_token(self, data: dict) -> str: pass
    
    @abstractmethod
    def create_refresh_token(self, data: dict) -> str: pass
    
    @abstractmethod
    def get_access_payload(self, token: str) -> Optional[dict]: pass
    
    @abstractmethod
    def get_refresh_payload(self, token: str) -> Optional[dict]: pass
    
    @abstractmethod
    def refresh_access_token(self, refresh_token: str) -> Optional[str]: pass