from abc import ABC, abstractmethod
from fastapi import Response
from typing import Optional

class ICookieService(ABC):
    @abstractmethod
    def set_cookie(self, response: Response, key: str, value: str, max_age: Optional[int] = None) -> None: pass

    @abstractmethod
    def delete_cookie(self, response: Response, key: str) -> None: pass