from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ClickStat(Base):
    __tablename__ = "click_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    short_url_id: Mapped[int] = mapped_column(
        ForeignKey("short_urls.id", ondelete="CASCADE"), nullable=False
    )
    clicked_at: Mapped[int] = mapped_column(nullable=False)
