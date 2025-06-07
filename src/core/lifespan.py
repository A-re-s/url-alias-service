from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.database import db_manager


@asynccontextmanager
async def db_init(app: FastAPI) -> AsyncGenerator[None, None]:
    await db_manager.connect()
    yield
    await db_manager.close()
