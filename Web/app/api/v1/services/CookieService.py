from fastapi import Response
from typing import Optional
from app.api.v1.interfaces import ICookieService

class CookieService(ICookieService):
    def __init__(
        self,
        secure: bool = False,
        httponly: bool = True,
        samesite: str = "strict"
    ):
        self.secure = secure
        self.httponly = httponly
        self.samesite = samesite

    def set_cookie(self, response: Response, key: str, value: str, max_age: Optional[int] = None) -> None:
        response.set_cookie(
            key=key,
            value=value,
            max_age=max_age,
            secure=self.secure,
            httponly=self.httponly,
            samesite=self.samesite)

    def delete_cookie(self, response: Response, key: str) -> None:
        response.delete_cookie(key=key)