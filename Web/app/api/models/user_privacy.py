from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Boolean, ForeignKey
from .base import Base

class UserPrivacyBase(Base):
    __tablename__ = "user_privacy"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    show_email: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    show_about: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["UserBase"] = relationship("UserBase", back_populates="privacy")