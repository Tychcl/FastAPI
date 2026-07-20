from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from .base import Base

class UserBase(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    about: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("user_roles.id"), nullable=False)
    role: Mapped["UserRoleBase"] = relationship("UserRoleBase", back_populates="users")

    privacy: Mapped["UserPrivacyBase"] = relationship(
        "UserPrivacyBase",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, email={self.email}, role_id={self.role_id})"

    @property
    def to_dict(self) -> dict:
        data: dict = super().to_dict
        data.pop('password', None)
        if self.role is not None:
            data['role'] = self.role.to_dict
        if self.privacy is not None:
            data['privacy'] = self.privacy.to_dict
        return data