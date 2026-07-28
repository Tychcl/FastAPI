from abc import ABC, abstractmethod

class IPasswordHasherService(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:pass
    
    @abstractmethod
    def verify(self, password: str, hash: str) -> bool: pass