import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api.v1.dependencies import get_uow
from db.database import Base
from src.main import app
from utils.unitofwork import UnitOfWork


@pytest_asyncio.fixture(scope="function")
async def async_client():

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    test_session_maker = async_sessionmaker(bind=test_engine, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def override_get_uow():
        return UnitOfWork(test_session_maker)

    app.dependency_overrides[get_uow] = override_get_uow

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
