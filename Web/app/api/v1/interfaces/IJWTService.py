from abc import ABC, abstractmethod

class IJWTService(ABC):
    @abstractmethod
    def create_access_token(self, data: dict) -> str: pass
    
    @abstractmethod
    def create_refresh_token(self, data: dict) -> str: pass
    
    @abstractmethod
    def get_access_payload(self, token: str) -> dict | None: pass
    
    @abstractmethod
    def get_refresh_payload(self, token: str) -> dict | None: pass
    
    @abstractmethod
    def refresh_access_token(self, refresh_token: str) -> str | None: pass