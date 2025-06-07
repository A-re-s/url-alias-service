from typing import Optional

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ShortURLModel(Base):
    __tablename__ = "short_urls"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    short_code: Mapped[Optional[str]] = mapped_column(
        unique=True, nullable=True, index=True
    )
    original_url: Mapped[str] = mapped_column(nullable=False)
    tag: Mapped[Optional[str]]
    clicks_left: Mapped[Optional[int]]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[int] = mapped_column(nullable=False)
