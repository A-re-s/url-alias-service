from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import get_settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(get_settings().db.database_url)
asycn_session_maker = async_sessionmaker(engine, expire_on_commit=False)
