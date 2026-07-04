from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from app.api.models.base import Base
from sqlalchemy.orm import relationship

class UserRoleBase(Base):
    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    users = relationship("UserBase", back_populates="role")