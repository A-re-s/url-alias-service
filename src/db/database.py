from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import Settings, get_settings


class Base(DeclarativeBase):
    pass


async def get_engine(
    settings: Annotated[Settings, Depends(get_settings)],
):
    engine = create_async_engine(settings.db.database_url)
    yield engine
    await engine.dispose()


async def get_session_maker(engine: Annotated[AsyncEngine, Depends(get_engine)]):
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    yield session_maker


async def get_async_session(
    session_maker: Annotated[async_sessionmaker, Depends(get_session_maker)],
):
    async with session_maker() as session:
        yield session


DBAsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
