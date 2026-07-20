from pydantic import BaseModel

class PrivacyUpdateRequest(BaseModel):
    show_email: bool
    show_about: bool