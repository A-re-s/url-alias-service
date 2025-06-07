from sqlalchemy import MetaData
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from config import get_settings
from models.base import Base


class DatabaseManager:
    def __init__(self, url: str | None = None) -> None:
        self.engine = create_async_engine(url)
        self.async_session_maker = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def connect(self) -> None:
        try:
            async with self.engine.begin() as conn:
                metadata = MetaData()
                await conn.run_sync(metadata.reflect)
                existing_tables = list(metadata.tables.keys())
                if not existing_tables:
                    await conn.run_sync(Base.metadata.create_all)
        except OperationalError as e:
            raise e

    async def close(self) -> None:
        await self.engine.dispose()


db_manager = DatabaseManager(get_settings().db.database_url)
