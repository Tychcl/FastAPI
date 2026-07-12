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

	id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
	username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
	email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
	password: Mapped[str] = mapped_column(String(), nullable=False)

	role_id: Mapped[int] = mapped_column(ForeignKey("user_roles.id"), nullable=False)
	role: ClassVar[UserRoleBase] = relationship("UserRoleBase", back_populates="users")

	def __repr__(self) -> dict:
		return {"id": self.id, "username": self.username, "email": self.email, "role_id": self.role_id, "role_name": self.role.name}

	@property
	def to_dict(self):
		return {"id": self.id, "username": self.username, "email": self.email, "role_id": self.role_id}