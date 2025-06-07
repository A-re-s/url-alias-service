from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    username: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    token_version: Mapped[int] = mapped_column(default=0)
