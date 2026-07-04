from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .user_role import UserRoleBase
from typing import ClassVar
from ..v1.requests import SignupRequest

class UserBase(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True)
	username: Mapped[str] = mapped_column(String(15))
	password: Mapped[str] = mapped_column(String())

	role_id: Mapped[int] = mapped_column(ForeignKey("user_roles.id"))
	role: ClassVar[UserRoleBase] = relationship("UserRoleBase", back_populates="users")

	def __repr__(self) -> str:
		return f"UserBase:id={self.id}, login={self.username}, password={self.password}, role_id={self.role_id}, role_name={self.role.name})"

	def from_signup_request(request: SignupRequest) -> "UserBase":
		return UserBase(
            username=request.username,
            password=request.password,
            role_id=request.role_id
        )